import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger("browser.browser_discovery")

def discover_browsers() -> List[Dict[str, Any]]:
    """
    Discover installed browsers and their profile information.
    
    Returns:
        List of browser dictionaries with name, executable path, user data directory, and profiles
    """
    browsers = []
    
    # Log platform information for debugging
    import sys
    logger.info(f"Platform detection in browser discovery: {sys.platform}")
    
    # Get environment variables for path resolution
    
    # Get environment variables for path resolution
    local_app_data = os.environ.get('LOCALAPPDATA', '')
    program_files = os.environ.get('PROGRAMFILES', '')
    program_files_x86 = os.environ.get('PROGRAMFILES(X86)', '')
    
    # Define supported browsers and their detection information
    browser_configs = [
        {
            "name": "Chrome",
            "executable_paths": [
                os.path.join(program_files, "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(program_files_x86, "Google", "Chrome", "Application", "chrome.exe")
            ],
            "user_data_path": os.path.join(local_app_data, "Google", "Chrome", "User Data")
        },
        {
            "name": "Edge",
            "executable_paths": [
                os.path.join(program_files, "Microsoft", "Edge", "Application", "msedge.exe"),
                os.path.join(program_files_x86, "Microsoft", "Edge", "Application", "msedge.exe")
            ],
            "user_data_path": os.path.join(local_app_data, "Microsoft", "Edge", "User Data")
        },
        {
            "name": "Brave",
            "executable_paths": [
                os.path.join(program_files, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
                os.path.join(program_files_x86, "BraveSoftware", "Brave-Browser", "Application", "brave.exe")
            ],
            "user_data_path": os.path.join(local_app_data, "BraveSoftware", "Brave-Browser", "User Data")
        }
    ]
    
    # Check each browser
    for config in browser_configs:
        browser_info = {
            "browser": config["name"],
            "installed": False,
            "executable": None,
            "user_data": config["user_data_path"],
            "profiles": []
        }
        
        logger.info(f"Checking for {config['name']}...")
        
        # Find executable path
        executable_path = None
        for exec_path in config["executable_paths"]:
            if os.path.exists(exec_path):
                executable_path = exec_path
                break
        
        if executable_path:
            browser_info["installed"] = True
            browser_info["executable"] = executable_path
            logger.info(f"  Detected {config['name']} executable: {executable_path}")
            
            # Check user data directory exists
            user_data_dir = config["user_data_path"]
            if os.path.exists(user_data_dir):
                logger.info(f"  Found User Data directory: {user_data_dir}")
                
                # Scan for profiles (only folders named "Default", "Profile 1", "Profile 2", etc.)
                profiles = []
                try:
                    items = os.listdir(user_data_dir)
                    for item in items:
                        item_path = os.path.join(user_data_dir, item)
                        if os.path.isdir(item_path):
                            # Only include standard profile names
                            if item in ["Default"] or (item.startswith("Profile ") and item[8:].isdigit()):
                                profiles.append(item)
                except Exception as e:
                    logger.error(f"Error scanning profiles for {config['name']}: {e}")
                
                browser_info["profiles"] = sorted(profiles)
                logger.info(f"  Found profiles: {profiles}")
            else:
                logger.info(f"  User Data directory not found: {user_data_dir}")
        else:
            logger.info(f"  {config['name']} executable not found")
        
        browsers.append(browser_info)
    
    return browsers