#!/usr/bin/env python3
"""
Script to inspect the real DOM of Hepsiburada cart coupon drawer.
This script opens the configured browser, navigates to the cart page,
opens the coupon drawer, and saves detailed element information.
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.async_api import async_playwright
from app.browser.browser_manager import BrowserManager


async def inspect_hepsiburada_cart_coupon_drawer():
    """Inspect the Hepsiburada cart coupon drawer DOM"""
    
    # Create artifacts directory if it doesn't exist
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(exist_ok=True)
    
    print("Starting Hepsiburada cart coupon drawer inspection...")
    
    try:
        # Initialize browser manager
        browser_manager = BrowserManager()
        
        # Check if browser is already running
        if browser_manager._browser is not None:
            print("Browser is already running")
        else:
            print("Starting browser...")
            await browser_manager.start()
            
        # Get the persistent context
        context = browser_manager.context
        
        if not context:
            print("No browser context available")
            return
            
        # Create a new page
        page = await context.new_page()
        
        # Navigate to the cart page with better wait condition
        print("Navigating to https://checkout.hepsiburada.com/sepetim...")
        await page.goto(
            "https://checkout.hepsiburada.com/sepetim",
            wait_until="domcontentloaded",
            timeout=30000
        )
        
        # Wait for DOM to be available 
        await page.wait_for_selector("body")
        print("Page loaded successfully")
        
        # Allow the cart's client-side UI to render
        await asyncio.sleep(1)
        
        # Locate the visible "Kupon kodu ekle" control
        print("Searching for 'Kupon kodu ekle' control...")
        
        # Try multiple resilient locators
        coupon_control = None
        locator_used = ""
        
        # Try by text content first (most reliable)
        coupon_control = page.get_by_text("Kupon kodu ekle")
        if await coupon_control.count() > 0:
            locator_used = "get_by_text('Kupon kodu ekle')"
        else:
            # Try by role and text
            coupon_control = page.get_by_role("button", name="Kupon kodu ekle")
            if await coupon_control.count() > 0:
                locator_used = "get_by_role('button', name='Kupon kodu ekle')"
            else:
                # Try aria-label matching
                coupon_control = page.get_by_aria_label("Kupon kodu ekle")
                if await coupon_control.count() > 0:
                    locator_used = "get_by_aria_label('Kupon kodu ekle')"
        
        print(f"Found using locator: {locator_used}")
        
        # Check if we found the control
        if await coupon_control.count() == 0:
            print("Coupon control not found. Make sure the configured browser profile has at least one product in the Hepsiburada cart.")
            return
            
        # Click the control to open the drawer
        print("Clicking 'Kupon kodu ekle' control...")
        await coupon_control.click()
        
        # Wait for the coupon drawer to become visible
        print("Waiting for coupon drawer to open...")
        await page.wait_for_timeout(1000)  # Give time for animation
        
        # Wait specifically for the coupon input to become visible
        coupon_input = page.get_by_placeholder("Kupon kodunuzu girin")
        if await coupon_input.count() > 0:
            print("Coupon input found in drawer")
        else:
            print("Coupon input not found in drawer")
            
        # Wait additional time for DOM to settle
        await asyncio.sleep(1)
        
        # Save full page content
        content = await page.content()
        html_output_file = artifacts_dir / "hepsiburada_cart_coupon_drawer.html"
        with open(html_output_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\nFull page content saved to {html_output_file}")
        
        # Get all elements from the DOM in one query
        print("\nCollecting all DOM elements...")
        
        # Execute JavaScript to get all elements with their attributes
        elements_data = await page.evaluate("""
            () => {
                const elements = document.querySelectorAll("*");
                const result = [];
                
                elements.forEach(element => {
                    const elementData = {
                        tagName: element.tagName.toLowerCase(),
                        id: element.id || "",
                        name: element.name || "",
                        type: element.type || "",
                        placeholder: element.placeholder || "",
                        role: element.role || "",
                        "aria-label": element.getAttribute("aria-label") || "",
                        "data-testid": element.getAttribute("data-testid") || "",
                        "data-test-id": element.getAttribute("data-test-id") || "",
                        class: element.className || "",
                        textContent: element.textContent.substring(0, 60).trim() || "",
                        href: element.href || "",
                        value: element.value || "",
                        disabled: element.disabled || false
                    };
                    
                    // Only include elements that have at least one attribute filled
                    if (Object.values(elementData).some(val => val !== "")) {
                        result.push(elementData);
                    }
                });
                
                return result;
            }
        """)
        
        # Save the complete inspection as JSON
        json_output_file = artifacts_dir / "hepsiburada_cart_coupon_drawer_dom.json"
        with open(json_output_file, "w", encoding="utf-8") as f:
            json.dump(elements_data, f, indent=2, ensure_ascii=False)
        print(f"DOM inventory saved to {json_output_file}")
        
        # Create focused inventory for coupon controls
        print("\nCreating focused coupon control inventory...")
        
        # Filter elements relevant to the coupon drawer
        coupon_controls = []
        for element in elements_data:
            # Include elements matching any of these characteristics:
            is_relevant = (
                element['tagName'] in ['input', 'button', 'textarea', 'select'] or
                element['role'] == 'button' or
                element['role'] == 'textbox' or
                element['placeholder'] is not None and element['placeholder'] != '' or
                element['data-testid'] is not None and element['data-testid'] != '' or
                element['data-test-id'] is not None and element['data-test-id'] != '' or
                (element['textContent'] is not None and ('Kupon' in element['textContent'] or 'kupon' in element['textContent'])) or
                (element['textContent'] is not None and 'Ekle' in element['textContent'])
            )
            
            if is_relevant:
                coupon_controls.append(element)
        
        # Save focused inventory
        focused_output_file = artifacts_dir / "hepsiburada_coupon_controls.json"
        with open(focused_output_file, "w", encoding="utf-8") as f:
            json.dump(coupon_controls, f, indent=2, ensure_ascii=False)
        print(f"Focused coupon controls saved to {focused_output_file}")
        
        # Print summary
        print("\nCOUPON CONTROL SUMMARY:")
        print(f"Current URL: {page.url}")
        print(f"'Kupon kodu ekle' found: {await coupon_control.count() > 0}")
        print(f"Coupon drawer opened: {await coupon_input.count() > 0}")
        print(f"Matching coupon inputs: {await coupon_input.count()}")
        print(f"Matching 'Ekle' buttons: {len([e for e in elements_data if e['tagName'] == 'button' and e['textContent'] and 'Ekle' in e['textContent']])}")
        
        print("\nFirst 5 coupon controls:")
        for i, elem in enumerate(coupon_controls[:5]):
            print(f"  [{i+1}] {elem['tagName']} - ID: '{elem['id']}' - Class: '{elem['class']}' - Text: '{elem['textContent']}'")
        
    except Exception as e:
        print(f"Error during inspection: {e}")
        raise
    finally:
        # Close the page but keep browser running for reuse
        if 'page' in locals():
            await page.close()
        print("\nInspection completed.")


if __name__ == "__main__":
    asyncio.run(inspect_hepsiburada_cart_coupon_drawer())
