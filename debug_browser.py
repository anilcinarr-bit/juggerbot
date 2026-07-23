#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the project root to Python path 
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.browser.browser_manager import BrowserManager

async def debug_browser():
    print("Creating BrowserManager instance...")
    bm = BrowserManager()
    
    print("Starting browser...")
    try:
        await bm.start()
        print("Browser started successfully")
    except Exception as e:
        print(f"Error starting browser: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_browser())