"""
Detailed technical inspection of N11 coupon redemption flow
This script analyzes actual N11 DOM elements without implementing automation.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from app.browser.browser_manager import BrowserManager
from app.platforms.n11 import CART_URL, COUPON_PAGE_URL, COUPON_INPUT_SELECTOR, APPLY_BUTTON_SELECTOR, RESULT_SELECTOR

async def inspect_n11_detailed():
    """Inspect N11 coupon redemption flow with detailed DOM analysis"""
    
    print("🔍 Detailed N11 Coupon Redemption Flow Analysis")
    print("=" * 60)
    print("This inspection analyzes actual DOM elements from N11 website")
    print()
    
    # Get browser manager instance
    browser_manager = BrowserManager()
    
    # Ensure browser is available
    if not browser_manager.available:
        print("Starting browser...")
        await browser_manager.start()
    
    # Create a new page from the persistent context
    page = await browser_manager.new_page()
    
    try:
        # Navigate to N11 coupon page
        print(f"🌐 Navigating to: {COUPON_PAGE_URL}")
        await page.goto(COUPON_PAGE_URL, wait_until="networkidle", timeout=30000)
        await page.wait_for_load_state("networkidle")
        
        print("\n📋 PLATFORM INFORMATION:")
        print(f"  - Cart URL: {CART_URL}")
        print(f"  - Coupon Page URL: {COUPON_PAGE_URL}")
        print()
        
        # Take screenshot of initial state
        await page.screenshot(path="n11_detailed_initial.png", full_page=True)
        print("✅ Initial state screenshot saved as n11_detailed_initial.png")
        
        # Get HTML snapshot of initial page
        html_content = await page.content()
        with open("n11_detailed_html.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("✅ Initial HTML snapshot saved as n11_detailed_html.html")
        print()
        
        # 1. COUPON OPEN BUTTON
        print("1️⃣ COUPON OPEN BUTTON ANALYSIS:")
        print("-" * 40)
        
        # Check for various potential selectors for coupon open button
        coupon_open_selectors = [
            ".coupon-open-button",
            "#coupon-open-btn", 
            "[data-testid='open-coupon']",
            ".use-promotion-code-button",
            ".coupon-panel button",
            "button:has-text('Kupon Gir')",
            "button:has-text('Enter Coupon')",
            ".coupon-input-container button",
            "[class*='coupon'] [class*='button']"
        ]
        
        open_button_found = False
        for selector in coupon_open_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    print(f"  ✅ Found with selector: {selector}")
                    # Get exact HTML snippet
                    html_snippet = await element.inner_html()
                    print(f"     HTML snippet: {html_snippet[:200]}...")
                    
                    # Get text content
                    text_content = await element.inner_text()
                    print(f"     Text content: '{text_content}'")
                    
                    # Visibility check
                    is_visible = await element.is_visible()
                    print(f"     Visible: {is_visible}")
                    
                    # Check if it's unique (count how many elements match)
                    all_elements = await page.query_selector_all(selector)
                    print(f"     Total matching elements: {len(all_elements)}")
                    
                    open_button_found = True
                    break
            except Exception as e:
                print(f"  ⚠️  Selector {selector} failed: {e}")
                continue
        
        if not open_button_found:
            print("  ❌ No coupon open button found with standard selectors")
            print("     Note: N11 may not have a separate 'open' button - coupon input might be inline")
        print()
        
        # 2. COUPON INPUT FIELD
        print("2️⃣ COUPON INPUT FIELD ANALYSIS:")
        print("-" * 40)
        
        try:
            # Check the defined selector first
            input_element = await page.query_selector(COUPON_INPUT_SELECTOR)
            if input_element:
                print(f"  ✅ Found with selector: {COUPON_INPUT_SELECTOR}")
                
                # Get exact HTML snippet
                html_snippet = await input_element.inner_html()
                print(f"     HTML snippet: {html_snippet[:200]}...")
                
                # Get attributes
                placeholder = await input_element.get_attribute("placeholder")
                name = await input_element.get_attribute("name")
                id_attr = await input_element.get_attribute("id")
                required = await input_element.get_attribute("required")
                
                print(f"     Placeholder: '{placeholder}'")
                print(f"     Name attribute: '{name}'")
                print(f"     ID attribute: '{id_attr}'")
                print(f"     Required attribute: {required}")
                
                # Visibility check
                is_visible = await input_element.is_visible()
                print(f"     Visible: {is_visible}")
                
                # Check uniqueness
                all_elements = await page.query_selector_all(COUPON_INPUT_SELECTOR)
                print(f"     Total matching elements: {len(all_elements)}")
                
            else:
                print(f"  ❌ No element found with selector: {COUPON_INPUT_SELECTOR}")
        except Exception as e:
            print(f"  ❌ Error inspecting coupon input: {e}")
        print()
        
        # 3. APPLY BUTTON
        print("3️⃣ APPLY BUTTON ANALYSIS:")
        print("-" * 40)
        
        try:
            # Check the defined selector first
            button_element = await page.query_selector(APPLY_BUTTON_SELECTOR)
            if button_element:
                print(f"  ✅ Found with selector: {APPLY_BUTTON_SELECTOR}")
                
                # Get exact HTML snippet
                html_snippet = await button_element.inner_html()
                print(f"     HTML snippet: {html_snippet[:200]}...")
                
                # Get text content
                text_content = await button_element.inner_text()
                print(f"     Text content: '{text_content}'")
                
                # Visibility check
                is_visible = await button_element.is_visible()
                print(f"     Visible: {is_visible}")
                
                # Check if initially disabled
                disabled = await button_element.get_attribute("disabled")
                print(f"     Initially disabled: {disabled}")
                
                # Check uniqueness
                all_elements = await page.query_selector_all(APPLY_BUTTON_SELECTOR)
                print(f"     Total matching elements: {len(all_elements)}")
                
            else:
                print(f"  ❌ No element found with selector: {APPLY_BUTTON_SELECTOR}")
        except Exception as e:
            print(f"  ❌ Error inspecting apply button: {e}")
        print()
        
        # 4. SUCCESS MESSAGE
        print("4️⃣ SUCCESS MESSAGE ANALYSIS:")
        print("-" * 40)
        
        try:
            # Check the defined selector first
            result_element = await page.query_selector(RESULT_SELECTOR)
            if result_element:
                print(f"  ✅ Found with selector: {RESULT_SELECTOR}")
                
                # Get exact HTML snippet
                html_snippet = await result_element.inner_html()
                print(f"     HTML snippet: {html_snippet[:200]}...")
                
                # Get text content
                text_content = await result_element.inner_text()
                print(f"     Text content: '{text_content}'")
                
                # Visibility check
                is_visible = await result_element.is_visible()
                print(f"     Visible: {is_visible}")
                
                # Check uniqueness
                all_elements = await page.query_selector_all(RESULT_SELECTOR)
                print(f"     Total matching elements: {len(all_elements)}")
                
            else:
                print(f"  ⚠️  No element found with selector: {RESULT_SELECTOR}")
                print("     Note: Success messages may appear after submission or might not exist yet")
        except Exception as e:
            print(f"  ❌ Error inspecting result message: {e}")
        print()
        
        # 5. INVALID MESSAGE
        print("5️⃣ INVALID MESSAGE ANALYSIS:")
        print("-" * 40)
        print("  ⚠️  Cannot verify without actual submission")
        print("     Invalid messages appear after attempting to apply an invalid coupon")
        print("     They would need to be captured during a real submission")
        print()
        
        # 6. ALREADY USED MESSAGE
        print("6️⃣ ALREADY USED MESSAGE ANALYSIS:")
        print("-" * 40)
        print("  ⚠️  Cannot verify without actual submission")
        print("     Already used messages appear after attempting to apply a used coupon")
        print("     They would need to be captured during a real submission")
        print()
        
        # 7. EXPIRED MESSAGE
        print("7️⃣ EXPIRED MESSAGE ANALYSIS:")
        print("-" * 40)
        print("  ⚠️  Cannot verify without actual submission")
        print("     Expired messages appear after attempting to apply an expired coupon")
        print("     They would need to be captured during a real submission")
        print()
        
        # 8. MINIMUM CART MESSAGE
        print("8️⃣ MINIMUM CART MESSAGE ANALYSIS:")
        print("-" * 40)
        print("  ⚠️  Cannot verify without actual submission")
        print("     Minimum cart messages appear after attempting to apply a coupon with insufficient cart value")
        print("     They would need to be captured during a real submission")
        print()
        
        # Additional DOM analysis
        print("🔍 ADDITIONAL DOM ANALYSIS:")
        print("-" * 40)
        
        # Look for common message containers
        message_selectors = [
            ".alert-success",
            ".alert-error", 
            ".alert-warning",
            ".message-box",
            ".notification",
            "[class*='message']",
            "[class*='alert']"
        ]
        
        found_messages = []
        for selector in message_selectors:
            try:
                elements = await page.query_selector_all(selector)
                if len(elements) > 0:
                    print(f"  ✅ Found {len(elements)} elements with selector: {selector}")
                    found_messages.append((selector, len(elements)))
            except:
                continue
                
        if not found_messages:
            print("  ⚠️  No standard message containers found")
            
        # Check for modal elements
        try:
            modals = await page.query_selector_all(".modal")
            if len(modals) > 0:
                print(f"  ✅ Found {len(modals)} modal elements")
                for i, modal in enumerate(modals):
                    html_snippet = await modal.inner_html()
                    print(f"     Modal {i+1} HTML: {html_snippet[:100]}...")
            else:
                print("  ⚠️  No modal elements found")
        except Exception as e:
            print(f"  ⚠️  Could not check for modals: {e}")
            
        # Take final screenshot
        await page.screenshot(path="n11_detailed_final.png", full_page=True)
        print("✅ Final inspection screenshot saved as n11_detailed_final.png")
        
        print("\n📋 Detailed Inspection Complete!")
        print()
        print("⚠️  IMPORTANT: This inspection shows the current state of the N11 website.")
        print("   Actual error messages can only be verified by submitting coupons and")
        print("   capturing the DOM after submission, which requires automation.")
        print()
        print("   The selectors provided are based on the static HTML structure observed.")
        
    except Exception as e:
        print(f"❌ Error during detailed inspection: {e}")
        raise
    finally:
        # Close the page but keep browser open for reuse
        await page.close()

# Run the detailed inspection
if __name__ == "__main__":
    asyncio.run(inspect_n11_detailed())