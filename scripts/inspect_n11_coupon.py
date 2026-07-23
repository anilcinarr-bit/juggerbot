"""
Technical inspection of N11 coupon redemption flow
This script analyzes the N11 platform without implementing automation.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from app.browser.browser_manager import BrowserManager
from app.platforms.n11 import CART_URL, COUPON_PAGE_URL

async def inspect_n11_coupon_flow():
    """Inspect N11 coupon redemption flow"""
    
    print("🔍 Inspecting N11 Coupon Redemption Flow")
    print("=" * 50)
    
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
        
        print("\n📋 Platform Information:")
        print(f"  - Cart URL: {CART_URL}")
        print(f"  - Coupon Page URL: {COUPON_PAGE_URL}")
        
        # Take screenshot of initial state
        await page.screenshot(path="n11_initial_state.png", full_page=True)
        print("  ✅ Initial state screenshot saved as n11_initial_state.png")
        
        # Get HTML snapshot of initial page
        html_content = await page.content()
        with open("n11_initial_html.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("  ✅ Initial HTML snapshot saved as n11_initial_html.html")
        
        # Look for coupon open button (if it exists)
        print("\n🔍 Searching for Coupon Open Button:")
        try:
            # Try different selectors that might be relevant
            selectors_to_try = [
                ".coupon-open-button",
                "#coupon-open-btn", 
                "[data-testid='open-coupon']",
                ".use-promotion-code-button",
                ".coupon-panel button",
                "button:has-text('Kupon Gir')",
                "button:has-text('Enter Coupon')"
            ]
            
            button_found = False
            for selector in selectors_to_try:
                try:
                    button = await page.query_selector(selector)
                    if button:
                        print(f"  ✅ Found button with selector: {selector}")
                        # Get button properties
                        button_html = await button.inner_html()
                        print(f"     HTML snippet: {button_html[:100]}...")
                        button_text = await button.inner_text()
                        print(f"     Button text: '{button_text}'")
                        button_found = True
                        break
                except:
                    continue
            
            if not button_found:
                print("  ⚠️  No obvious coupon open button found - might be inline")
                
        except Exception as e:
            print(f"  ❌ Error finding coupon open button: {e}")
        
        # Look for coupon input field
        print("\n🔍 Searching for Coupon Input Field:")
        try:
            # Try different selectors that might be relevant
            selectors_to_try = [
                "#coupon-input",
                "input[name='coupon']",
                "[data-testid='coupon-input']",
                ".coupon-code-input",
                "input[placeholder*='Kupon']",
                "input[placeholder*='Coupon']"
            ]
            
            input_found = False
            for selector in selectors_to_try:
                try:
                    input_field = await page.query_selector(selector)
                    if input_field:
                        print(f"  ✅ Found input with selector: {selector}")
                        # Get input properties
                        placeholder = await input_field.get_attribute("placeholder")
                        name = await input_field.get_attribute("name")
                        id_attr = await input_field.get_attribute("id")
                        required = await input_field.get_attribute("required")
                        
                        print(f"     Placeholder: '{placeholder}'")
                        print(f"     Name: '{name}'")
                        print(f"     ID: '{id_attr}'")
                        print(f"     Required: {required}")
                        
                        # Get HTML snippet
                        input_html = await input_field.inner_html()
                        print(f"     HTML snippet: {input_html[:100]}...")
                        input_found = True
                        break
                except:
                    continue
            
            if not input_found:
                print("  ⚠️  No coupon input field found with standard selectors")
                
        except Exception as e:
            print(f"  ❌ Error finding coupon input: {e}")
        
        # Look for apply button
        print("\n🔍 Searching for Apply Button:")
        try:
            # Try different selectors that might be relevant
            selectors_to_try = [
                "#apply-coupon-button",
                "[data-testid='apply-coupon']",
                ".apply-coupon-btn",
                "button:has-text('Uygula')",
                "button:has-text('Apply')",
                "button[type='submit']"
            ]
            
            button_found = False
            for selector in selectors_to_try:
                try:
                    button = await page.query_selector(selector)
                    if button:
                        print(f"  ✅ Found apply button with selector: {selector}")
                        # Get button properties
                        button_html = await button.inner_html()
                        print(f"     HTML snippet: {button_html[:100]}...")
                        button_text = await button.inner_text()
                        print(f"     Button text: '{button_text}'")
                        
                        # Check if it's initially disabled
                        disabled = await button.get_attribute("disabled")
                        print(f"     Initially disabled: {disabled}")
                        
                        button_found = True
                        break
                except:
                    continue
            
            if not button_found:
                print("  ⚠️  No apply button found with standard selectors")
                
        except Exception as e:
            print(f"  ❌ Error finding apply button: {e}")
        
        # Look for result messages
        print("\n🔍 Searching for Result Messages:")
        try:
            # Try different selectors that might be relevant for results
            selectors_to_try = [
                ".coupon-result-message",
                "[data-testid='coupon-result']",
                ".alert-success",
                ".alert-error",
                ".message-box",
                ".notification",
                "#result-message"
            ]
            
            result_found = False
            for selector in selectors_to_try:
                try:
                    result_element = await page.query_selector(selector)
                    if result_element:
                        print(f"  ✅ Found result element with selector: {selector}")
                        # Get result properties
                        result_html = await result_element.inner_html()
                        print(f"     HTML snippet: {result_html[:100]}...")
                        result_text = await result_element.inner_text()
                        print(f"     Text content: '{result_text}'")
                        
                        result_found = True
                        break
                except:
                    continue
            
            if not result_found:
                print("  ⚠️  No specific result messages found - might appear inline or via DOM changes")
                
        except Exception as e:
            print(f"  ❌ Error finding result messages: {e}")
        
        # Analyze page structure for different types of notifications
        print("\n🔍 Analyzing Notification Types:")
        
        # Check for modal elements
        try:
            modals = await page.query_selector_all(".modal")
            if len(modals) > 0:
                print("  ✅ Modal elements detected")
                for i, modal in enumerate(modals):
                    modal_html = await modal.inner_html()
                    print(f"     Modal {i+1} HTML snippet: {modal_html[:100]}...")
            else:
                print("  ⚠️  No modal elements found")
        except:
            print("  ⚠️  Could not check for modals")
        
        # Check for toast notifications
        try:
            toasts = await page.query_selector_all(".toast")
            if len(toasts) > 0:
                print("  ✅ Toast notifications detected")
                for i, toast in enumerate(toasts):
                    toast_html = await toast.inner_html()
                    print(f"     Toast {i+1} HTML snippet: {toast_html[:100]}...")
            else:
                print("  ⚠️  No toast notifications found")
        except:
            print("  ⚠️  Could not check for toasts")
            
        # Check for alert elements
        try:
            alerts = await page.query_selector_all(".alert")
            if len(alerts) > 0:
                print("  ✅ Alert elements detected")
                for i, alert in enumerate(alerts):
                    alert_html = await alert.inner_html()
                    print(f"     Alert {i+1} HTML snippet: {alert_html[:100]}...")
            else:
                print("  ⚠️  No alert elements found")
        except:
            print("  ⚠️  Could not check for alerts")
        
        # Take final screenshot
        await page.screenshot(path="n11_final_inspection.png", full_page=True)
        print("  ✅ Final inspection screenshot saved as n11_final_inspection.png")
        
        print("\n📋 Inspection Complete!")
        
    except Exception as e:
        print(f"❌ Error during inspection: {e}")
        raise
    finally:
        # Close the page but keep browser open for reuse
        await page.close()

# Run the inspection
if __name__ == "__main__":
    asyncio.run(inspect_n11_coupon_flow())