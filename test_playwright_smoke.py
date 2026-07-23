#!/usr/bin/env python3
"""
Standalone Playwright smoke test to diagnose Windows asyncio compatibility issues.
This script tests if Playwright can start successfully in isolation from the main application.
"""

import asyncio
import sys
from playwright.async_api import async_playwright

async def test_playwright():
    """Test Playwright startup and basic functionality"""
    print("Starting Playwright test...")
    
    try:
        # Start Playwright
        print("1. Starting Playwright...")
        pw = await async_playwright().start()
        print("2. Playwright started successfully")
        
        # Launch Chromium browser (headed mode)
        print("3. Launching Chromium browser...")
        browser = await pw.chromium.launch(headless=False)
        print("4. Browser launched successfully")
        
        # Open example.com
        print("5. Opening https://example.com...")
        page = await browser.new_page()
        await page.goto("https://example.com")
        print("6. Page loaded successfully")
        
        # Wait 5 seconds to observe the browser window
        print("7. Waiting 5 seconds...")
        await asyncio.sleep(5)
        print("8. Sleep completed")
        
        # Close browser
        print("9. Closing browser...")
        await browser.close()
        print("10. Browser closed successfully")
        
        # Stop Playwright
        print("11. Stopping Playwright...")
        await pw.stop()
        print("12. Playwright stopped successfully")
        
        print("\n✅ SUCCESS: Playwright test completed without errors!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Playwright test failed with exception: {e}")
        print(f"Exception type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running standalone Playwright smoke test...")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    try:
        result = asyncio.run(test_playwright())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"Failed to run test: {e}")
        sys.exit(1)