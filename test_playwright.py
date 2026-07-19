#!/usr/bin/env python
"""Direct test of Playwright on Windows to isolate the issue"""

import asyncio
import sys
import logging

# Set up logging 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_playwright():
    print(f"Platform: {sys.platform}")
    print(f"Current event loop: {type(asyncio.get_running_loop())}")
    print(f"Current policy: {type(asyncio.get_event_loop_policy())}")
    
    try:
        from playwright.async_api import async_playwright
        print("About to start Playwright...")
        pw = await async_playwright().start()
        print("Playwright started successfully!")
        
        browser = await pw.chromium.launch(headless=True)
        print("Browser launched successfully!")
        
        context = await browser.new_context()
        page = await context.new_page()
        print("Page created successfully!")
        
        await browser.close()
        await pw.stop()
        print("All cleaned up successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_playwright())