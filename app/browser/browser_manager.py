import logging
from typing import Optional
from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext, Page

from app.browser.exceptions import BrowserUnavailable, BrowserNotConfigured
from app.browser.browser_config import load_browser_config
from app.browser.browser_discovery import discover_browsers

logger = logging.getLogger("browser.browser_manager")


class BrowserManager:
    """Manages browser lifecycle using Playwright - Singleton pattern"""
    
    _instance: Optional['BrowserManager'] = None
    
    def __new__(cls) -> 'BrowserManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize BrowserManager with singleton pattern"""
        if not hasattr(self, '_initialized'):
            self._playwright: Optional[Playwright] = None
            self._browser: Optional[Browser] = None
            self._persistent_context: Optional[BrowserContext] = None
            self._available: bool = False
            self._initialized = True
    
    @property
    def available(self) -> bool:
        """Check if browser is available for use"""
        return self._available
    
    @property
    def browser(self) -> Optional[Browser]:
        """Get the browser instance"""
        if not self._available:
            raise BrowserUnavailable("Browser is not available. Check if it started correctly.")
        return self._browser
        
    @property
    def context(self) -> Optional[BrowserContext]:
        """Get the persistent browser context"""
        if not self._available:
            raise BrowserUnavailable("Browser is not available. Check if it started correctly.")
        return self._persistent_context
        
    @property
    def page(self) -> Optional[Page]:
        """Get the browser page"""
        if not self._available:
            raise BrowserUnavailable("Browser is not available. Check if it started correctly.")
        return self._page
    
    async def new_page(self) -> Page:
        """Create a new page from the persistent context (this is what adapters should use)"""
        if not self._available or not self._persistent_context:
            raise BrowserUnavailable("Browser is not available. Cannot create new page.")
        
        logger.info("Creating new page from persistent context")
        return await self._persistent_context.new_page()
    
    async def get_context_for_platform(self, platform: str) -> BrowserContext:
        """Get the persistent browser context for automation (no new contexts created)"""
        if not self._available:
            raise BrowserUnavailable("Browser is not available. Check if it started correctly.")
        
        # Always return the persistent context - never create new ones
        logger.info(f"Using persistent browser context for {platform}")
        return self._persistent_context
    
    async def start(self) -> None:
        """Start the browser manager with persistent sessions"""
        # Check if browser is already running
        if self._browser is not None:
            logger.info("Browser is already running. Skipping start.")
            return
            
        logger.info("Browser starting...")
        
        try:
            # Initialize Playwright - this may fail on Windows due to event loop issues
            self._playwright = await async_playwright().start()
            
            # Load configuration
            config = load_browser_config()
            logger.info(f"Selected browser: {config.selected_browser}")
            logger.info(f"Selected profile: {config.selected_profile}")
            
            # Check if browser/profile are configured
            if config.selected_browser is None or config.selected_profile is None:
                raise BrowserNotConfigured("No browser/profile has been configured yet.")
            
            # Discover browsers
            browsers = discover_browsers()
            
            # Find the configured browser
            selected_browser = None
            for browser in browsers:
                if browser["browser"] == config.selected_browser and browser["installed"]:
                    selected_browser = browser
                    break
            
            if not selected_browser:
                raise FileNotFoundError(f"Configured browser '{config.selected_browser}' not found. Please install the browser or update your configuration.")
            
            # Validate profile exists
            if config.selected_profile and config.selected_profile not in selected_browser["profiles"]:
                raise FileNotFoundError(f"Configured profile '{config.selected_profile}' not found for browser '{config.selected_browser}'.")
            
            # Launch browser with persistent context using configuration
            logger.info("Loading browser with persistent context...")
            logger.info(f"Resolved executable_path: {selected_browser['executable']}")
            logger.info(f"Resolved user_data_dir: {selected_browser['user_data']}")
            
            self._persistent_context = await self._playwright.chromium.launch_persistent_context(
                executable_path=selected_browser["executable"],
                user_data_dir=selected_browser["user_data"],
                headless=False,  # Run in headed mode for development
                timeout=30000    # 30 second timeout
            )
            
            # Set the browser instance from the persistent context
            self._browser = self._persistent_context.browser
            
            self._available = True
            logger.info("Browser started successfully with persistent context.")
            
        except NotImplementedError as e:
            # This is the specific error we're trying to fix
            if sys.platform == "win32":
                logger.error("Playwright subprocess error on Windows - this is a known limitation with Uvicorn/asyncio event loops")
                logger.error("Continuing without browser functionality (per requirements)")
                # Re-raise to signal the error but don't crash the app
                raise
            else:
                # For non-Windows, re-raise normally
                raise
                
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            # Re-raise the exception instead of silently failing - this ensures proper error handling 
            raise
    
    async def stop(self) -> None:
        """Stop the browser manager and clean up browser components"""
        # Check if browser is already stopped
        if self._browser is None:
            logger.info("Browser is already stopped. Skipping stop.")
            return
            
        logger.info("Browser closing...")
        
        try:
            # Close persistent context
            if self._persistent_context:
                await self._persistent_context.close()
                self._persistent_context = None
            
            # Close browser
            if self._browser:
                await self._browser.close()
                self._browser = None
                
            # Stop Playwright
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
                
            logger.info("Browser closed.")
            
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
            raise



