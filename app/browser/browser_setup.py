import logging
from typing import List, Dict, Any
from app.browser.browser_config import load_browser_config, save_browser_config
from app.browser.browser_discovery import discover_browsers

logger = logging.getLogger("browser.browser_setup")

class BrowserNotFound(Exception):
    """Exception raised when a browser is not found"""
    pass

class ProfileNotFound(Exception):
    """Exception raised when a profile is not found"""
    pass

def get_available_browsers() -> List[Dict[str, Any]]:
    """
    Get list of available browsers.
    
    Returns:
        List of browser dictionaries from discover_browsers()
    """
    logger.info("Retrieving available browsers...")
    return discover_browsers()

def select_browser(browser_name: str) -> None:
    """
    Select a browser to use.
    
    Args:
        browser_name: Name of the browser to select
        
    Raises:
        BrowserNotFound: If the specified browser is not found
    """
    logger.info(f"Selecting browser: {browser_name}")
    
    # Validate that browser exists
    browsers = discover_browsers()
    browser_exists = any(browser["browser"] == browser_name and browser["installed"] for browser in browsers)
    
    if not browser_exists:
        raise BrowserNotFound(f"Browser '{browser_name}' not found")
    
    # Load current config
    config = load_browser_config()
    
    # Set selected browser
    config.selected_browser = browser_name
    
    # Save configuration
    save_browser_config(config)
    
    logger.info(f"Selected browser: {browser_name}")

def get_profiles(browser_name: str) -> List[str]:
    """
    Get list of profiles for a specific browser.
    
    Args:
        browser_name: Name of the browser to get profiles for
        
    Returns:
        List of profile names
        
    Raises:
        BrowserNotFound: If the specified browser is not found
    """
    logger.info(f"Retrieving profiles for browser: {browser_name}")
    
    # Validate that browser exists
    browsers = discover_browsers()
    browser_info = next((browser for browser in browsers if browser["browser"] == browser_name and browser["installed"]), None)
    
    if not browser_info:
        raise BrowserNotFound(f"Browser '{browser_name}' not found")
    
    return browser_info["profiles"]

def select_profile(profile_name: str) -> None:
    """
    Select a profile to use.
    
    Args:
        profile_name: Name of the profile to select
        
    Raises:
        ProfileNotFound: If the specified profile is not found
    """
    logger.info(f"Selecting profile: {profile_name}")
    
    # Load current config
    config = load_browser_config()
    
    # Validate that browser is selected first
    if not config.selected_browser:
        raise ProfileNotFound("Cannot select profile without selecting a browser first")
    
    # Validate that profile exists for the selected browser
    profiles = get_profiles(config.selected_browser)
    
    if profile_name not in profiles:
        raise ProfileNotFound(f"Profile '{profile_name}' not found for browser '{config.selected_browser}'")
    
    # Set selected profile
    config.selected_profile = profile_name
    
    # Save configuration
    save_browser_config(config)
    
    logger.info(f"Selected profile: {profile_name}")

def complete_setup() -> None:
    """
    Complete the setup process by marking first_run_completed as True.
    """
    logger.info("Completing setup...")
    
    # Load current config
    config = load_browser_config()
    
    # Mark setup as completed
    config.first_run_completed = True
    
    # Save configuration
    save_browser_config(config)
    
    logger.info("Setup completed successfully")