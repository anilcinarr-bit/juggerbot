#!/usr/bin/env python3
"""
Temporary development helper script to configure browser settings.
This script uses the existing browser setup service to configure Brave browser 
with Default profile for manual testing purposes.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path so we can run directly with python scripts/configure_browser_test.py
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.browser.browser_setup import select_browser, select_profile, complete_setup
from app.browser.browser_config import load_browser_config

def configure_browser():
    """Configure browser settings using the existing setup service"""
    
    print("Configuring browser through setup service...")
    
    # Configure browser and profile using existing API
    select_browser("Brave")
    select_profile("Default")
    complete_setup()
    
    # Load configuration to verify it was saved correctly
    config = load_browser_config()
    
    print(f"Selected browser: {config.selected_browser}")
    print(f"Selected profile: {config.selected_profile}")
    print(f"First run completed: {config.first_run_completed}")

if __name__ == "__main__":
    configure_browser()