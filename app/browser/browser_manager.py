import logging
import sys
import asyncio
import time
import subprocess
import os
from typing import Optional, Dict, Any, List
from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext, Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from app.browser.exceptions import BrowserUnavailable, BrowserNotConfigured
from app.browser.browser_config import load_browser_config, save_browser_config
from app.browser.browser_discovery import discover_browsers
from app.core.logging import logger

logger = logging.getLogger("browser.browser_manager")


class BrowserManager:
    """Manages browser lifecycle using CDP - Singleton pattern"""
    
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
            self._context: Optional[BrowserContext] = None
            self._available: bool = False
            self._automation_tab: Optional[Page] = None
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
        """Get the browser context"""
        if not self._available:
            raise BrowserUnavailable("Browser is not available. Check if it started correctly.")
        return self._context
    
    @property
    def page(self) -> Optional[Page]:
        """Get the current automation tab page"""
        if not self._available:
            raise BrowserUnavailable("Browser is not available. Check if it started correctly.")
        return self._automation_tab
    
    async def new_page(self) -> Page:
        """Create a new automation tab from the browser context"""
        if not self._available or not self._context:
            raise BrowserUnavailable("Browser is not available. Cannot create new page.")
        
        # Create a new automation tab (this will be closed when automation finishes)
        logger.info("Creating new automation tab")
        automation_page = await self._context.new_page()
        self._automation_tab = automation_page
        return automation_page
    
    async def get_context_for_platform(self, platform: str) -> BrowserContext:
        """Get the browser context for automation (no new contexts created)"""
        if not self._available:
            raise BrowserUnavailable("Browser is not available. Check if it started correctly.")
        
        # Always return the same context - never create new ones
        logger.info(f"Using browser context for {platform}")
        return self._context
    
    async def _detect_brave_browser(self) -> Optional[Dict[str, Any]]:
        """Detect if Brave browser is installed and get its information"""
        browsers = discover_browsers()
        
        # Find Brave specifically
        for browser in browsers:
            if browser["browser"] == "Brave" and browser["installed"]:
                return browser
        
        return None
    
    async def _check_cdp_connection(self, port: int) -> bool:
        """Check if CDP is available on the specified port"""
        # Simple socket-based check to avoid expensive Playwright instantiation
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.debug(f"CDP connection failed on port {port}: {e}")
            return False
    
    async def _start_brave_with_cdp(self, executable_path: str, user_data_dir: str, profile_name: str) -> int:
        """Start Brave browser with CDP enabled"""
        # Find available port (9222 is the default)
        port = 9222
        
        try:
            # Check if port is already in use
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                # Port is in use, try to find another one
                for i in range(9223, 9300):
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    result = sock.connect_ex(('localhost', i))
                    sock.close()
                    if result != 0:
                        port = i
                        break
        
        except Exception as e:
            logger.warning(f"Could not find available port: {e}")
        
        try:
            # Start Brave with CDP enabled using the user's profile
            cmd = [
                executable_path,
                f"--remote-debugging-port={port}",
                f"--user-data-dir={user_data_dir}",
                f"--profile-directory={profile_name}",
                "--no-first-run",
                "--disable-default-apps"
            ]
            
            logger.info(f"Starting Brave with CDP: {' '.join(cmd)}")
            
            # Start the process without waiting for it to complete
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            # Wait for CDP to become available (max 10 seconds)
            max_wait_time = 10  # seconds
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                if await self._check_cdp_connection(port):
                    logger.info(f"Successfully connected to Brave CDP on port {port}")
                    return port
                await asyncio.sleep(0.5)
            
            # If we get here, CDP connection timed out
            raise TimeoutError(f"Failed to connect to Brave CDP after {max_wait_time} seconds")
            
        except Exception as e:
            logger.error(f"Failed to start Brave with CDP: {e}")
            raise
    
    async def _connect_to_existing_brave(self, executable_path: str, user_data_dir: str, profile_name: str) -> int:
        """Check if Brave is already running and try to connect via CDP"""
        # Try connecting to default port first
        if await self._check_cdp_connection(9222):
            return 9222
        
        # If that fails, try starting Brave with CDP
        logger.info("No existing CDP connection found, starting Brave with CDP")
        return await self._start_brave_with_cdp(executable_path, user_data_dir, profile_name)
    
    async def start(self) -> None:
        """Start the browser manager using CDP-based approach"""
        # Check if browser is already running
        if self._browser is not None:
            logger.info("Browser is already running. Skipping start.")
            return
            
        logger.info("Starting browser manager with CDP approach...")
        
        try:
            # Initialize Playwright
            self._playwright = await async_playwright().start()
            
            # Load configuration
            config = load_browser_config()
            logger.info(f"Selected browser: {config.selected_browser}")
            logger.info(f"Selected profile: {config.selected_profile}")
            
            # Check if browser/profile are configured
            if config.selected_browser is None or config.selected_profile is None:
                raise BrowserNotConfigured("No browser/profile has been configured yet.")
            
            # Detect Brave browser
            brave_browser = await self._detect_brave_browser()
            if not brave_browser:
                raise FileNotFoundError("Brave browser not found. Please install Brave browser.")
            
            logger.info(f"Detected Brave executable: {brave_browser['executable']}")
            logger.info(f"Using user data directory: {brave_browser['user_data']}")
            
            # Connect to existing Brave or start a new one with CDP
            port = await self._connect_to_existing_brave(
                brave_browser["executable"], 
                brave_browser["user_data"],
                config.selected_profile
            )
            
            # Connect to the browser via CDP
            logger.info(f"Connecting to Brave via CDP on port {port}")
            self._browser = await self._playwright.chromium.connect_over_cdp(f"http://localhost:{port}")
            
            # Get existing context (don't create new one)
            logger.info("Getting existing browser context")
            if not self._browser.contexts:
                raise RuntimeError("No browser contexts found")
            self._context = self._browser.contexts[0]
            
            self._available = True
            logger.info("Browser started successfully with CDP connection.")
            
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
            # Close automation tab if it exists
            if self._automation_tab:
                await self._automation_tab.close()
                self._automation_tab = None
            
            # DO NOT close the context - it belongs to the user's real browser
            # Only clean up Playwright resources
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
                
            logger.info("Browser manager cleaned up, user browser left running.")
            
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
            raise
