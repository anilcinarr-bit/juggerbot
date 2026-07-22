import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger("browser.browser_config")

# Configuration file path
CONFIG_FILE_PATH = "data/config/browser.json"

class BrowserConfig:
    """Configuration model for browser settings"""
    
    def __init__(self):
        self.selected_browser: Optional[str] = None
        self.selected_profile: Optional[str] = None
        self.first_run_completed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "selected_browser": self.selected_browser,
            "selected_profile": self.selected_profile,
            "first_run_completed": self.first_run_completed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BrowserConfig':
        """Create configuration from dictionary"""
        config = cls()
        config.selected_browser = data.get("selected_browser")
        config.selected_profile = data.get("selected_profile")
        config.first_run_completed = data.get("first_run_completed", False)
        return config

def load_browser_config() -> BrowserConfig:
    """
    Load browser configuration from file.
    
    Returns:
        BrowserConfig object with loaded settings or default values
    """
    logger.info("Loading browser configuration...")
    
    # Create directories if they don't exist
    Path(CONFIG_FILE_PATH).parent.mkdir(parents=True, exist_ok=True)
    
    # Check if config file exists
    if not os.path.exists(CONFIG_FILE_PATH):
        logger.info("Browser configuration file not found. Using default settings.")
        # Return default configuration (first_run_completed = False)
        return BrowserConfig()
    
    try:
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        config = BrowserConfig.from_dict(data)
        logger.info(f"Loaded browser configuration: {config.to_dict()}")
        
        # Validate configuration
        if config.selected_browser and not validate_browser_installed(config.selected_browser):
            logger.warning(f"Selected browser '{config.selected_browser}' is no longer installed.")
            return BrowserConfig()  # Return default invalid state
        
        if config.selected_profile and not validate_profile_exists(config.selected_browser, config.selected_profile):
            logger.warning(f"Selected profile '{config.selected_profile}' for browser '{config.selected_browser}' does not exist.")
            return BrowserConfig()  # Return default invalid state
            
        return config
        
    except Exception as e:
        logger.error(f"Error loading browser configuration: {e}")
        return BrowserConfig()

def save_browser_config(config: BrowserConfig) -> None:
    """
    Save browser configuration to file.
    
    Args:
        config: BrowserConfig object to save
    """
    logger.info("Saving browser configuration...")
    
    # Create directories if they don't exist
    Path(CONFIG_FILE_PATH).parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info("Browser configuration saved successfully.")
        
    except Exception as e:
        logger.error(f"Error saving browser configuration: {e}")
        raise

def is_first_run() -> bool:
    """
    Check if this is the first run of the application.
    
    Returns:
        True if this is the first run, False otherwise
    """
    config = load_browser_config()
    return not config.first_run_completed

def validate_browser_installed(browser_name: str) -> bool:
    """
    Validate if a browser is installed.
    
    Args:
        browser_name: Name of the browser to check
        
    Returns:
        True if browser is installed, False otherwise
    """
    # This function would be implemented based on the discovery module
    # For now, we'll just log and return True as this sprint doesn't require implementation yet
    logger.info(f"Checking if browser '{browser_name}' is installed...")
    return True

def validate_profile_exists(browser_name: str, profile_name: str) -> bool:
    """
    Validate if a profile exists for the specified browser.
    
    Args:
        browser_name: Name of the browser
        profile_name: Name of the profile to check
        
    Returns:
        True if profile exists, False otherwise
    """
    # This function would be implemented based on the discovery module
    # For now, we'll just log and return True as this sprint doesn't require implementation yet
    logger.info(f"Checking if profile '{profile_name}' exists for browser '{browser_name}'...")
    return True