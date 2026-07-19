#!/usr/bin/env python3
"""Direct test of browser manager to debug Windows Playwright issue."""

import sys
import asyncio
import logging

# Set event loop policy before importing anything else
if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        print("Successfully set WindowsProactorEventLoopPolicy")
    except Exception as e:
        print(f"Failed to set WindowsProactorEventLoopPolicy: {e}")

# Configure logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.browser.browser_manager import BrowserManager

async def test_browser_manager():
    """Test browser manager directly."""
    print("Creating BrowserManager instance...")
    
    # Create the singleton instance
    browser_manager = BrowserManager()
    print(f"BrowserManager created: {browser_manager}")
    print(f"Available: {browser_manager.available}")
    
    try:
        print("Attempting to start browser...")
        await browser_manager.start()
        print("Browser started successfully!")
        print(f"Available after start: {browser_manager.available}")
    except Exception as e:
        print(f"Error starting browser: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_browser_manager())