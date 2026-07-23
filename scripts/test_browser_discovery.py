#!/usr/bin/env python3
"""
Test script for browser discovery and configuration
"""

import sys
import os

# Add the project root to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from app.browser.browser_discovery import discover_browsers
from app.browser.browser_config import load_browser_config

def main():
    """Main test function"""
    print("=== Browser Discovery Test ===")
    
    # Discover browsers
    browsers = discover_browsers()
    
    print("\nDetected browsers:")
    print("-" * 50)
    
    for browser in browsers:
        print(f"Browser: {browser['browser']}")
        print(f"Installed: {browser['installed']}")
        if browser['executable']:
            print(f"Executable: {browser['executable']}")
        if browser['user_data']:
            print(f"User Data: {browser['user_data']}")
        print(f"Profiles: {browser['profiles']}")
        print("-" * 50)
    
    # Load configuration
    print("\n=== Browser Configuration ===")
    config = load_browser_config()
    
    print(f"Selected browser: {config.selected_browser}")
    print(f"Selected profile: {config.selected_profile}")
    print(f"First run: {config.first_run_completed}")
    
    print("\nTest completed successfully.")

if __name__ == "__main__":
    main()