#!/usr/bin/env python3
"""
CDP Test Script - Connects to existing Microsoft Edge instance
"""

import asyncio
from playwright.async_api import async_playwright

async def main():
    """Connect to existing browser and test functionality"""
    print("Connecting to existing browser at http://127.0.0.1:9222...")
    
    try:
        async with async_playwright() as p:
            # Connect to the existing browser instance
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            
            print("\nConnected to browser!")
            print(f"Browser version: {await browser.version()}")
            
            # Get the default context (this represents the browser session)
            contexts = browser.contexts
            print(f"\nNumber of contexts: {len(contexts)}")
            
            if contexts:
                # Get the first context (there should be one for the main browser session)
                context = contexts[0]
                
                # List all open pages/tabs
                print("\nOpen tabs:")
                pages = context.pages
                for i, page in enumerate(pages):
                    title = await page.title()
                    url = page.url
                    print(f"  {i}: Title: {title}, URL: {url}")
                
                # Open a new tab
                print("\nOpening new tab...")
                new_page = await context.new_page()
                
                # Navigate to example.com
                print("Navigating to https://example.com...")
                await new_page.goto("https://example.com", wait_until="networkidle")
                
                # Print the title of the new page
                title = await new_page.title()
                print(f"New tab title: {title}")
                
                # Close the new tab
                await new_page.close()
                print("\nNew tab closed.")
            
            # Disconnect from browser
            await browser.close()
            print("\nDisconnected from browser.")
            
    except Exception as e:
        print(f"Error connecting to browser: {e}")

if __name__ == "__main__":
    asyncio.run(main())