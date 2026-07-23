import asyncio
import sys
import os
import json
from playwright.async_api import async_playwright, Page

# Add the project root to Python path - fix for direct execution
project_root = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(project_root)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app.browser.browser_manager import BrowserManager

async def inspect_trendyol_coupon_page():
    """Inspect Trendyol coupon page elements for automation - FINAL CORRECTED VERSION"""
    
    try:
        # Initialize browser manager with existing configuration
        print("Initializing browser manager...")
        browser_manager = BrowserManager()
        
        # Start the browser using existing persistent context (this will use Brave profile)
        print("Starting browser with existing persistent context...")
        await browser_manager.start()
        
        # Get a new page from the persistent context (this is how adapters should work)
        print("Getting new page from persistent context...")
        page = await browser_manager.new_page()
        
        # Navigate to cart page directly since that's where coupons would be
        print("Navigating to cart page to inspect coupon area...")
        await page.goto("https://www.trendyol.com/sepet", wait_until="networkidle", timeout=30000)
        
        # Wait for page to fully load
        await asyncio.sleep(2)
        
        # Collect ALL input and button elements on the page for inspection
        print("Collecting all DOM elements for inspection...")
        
        # Get all input elements 
        input_elements = await page.query_selector_all("input")
        input_details = []
        
        # Get all button elements
        button_elements = await page.query_selector_all("button")
        button_details = []
        
        # Collect detailed information about each input element
        for i, element in enumerate(input_elements):
            try:
                tag = await element.get_attribute("tagname") or "input"
                input_type = await element.get_attribute("type") or ""
                placeholder = await element.get_attribute("placeholder") or ""
                name = await element.get_attribute("name") or ""
                element_id = await element.get_attribute("id") or ""
                class_attr = await element.get_attribute("class") or ""
                aria_label = await element.get_attribute("aria-label") or ""
                
                # Get closest parent classes
                parent_classes = ""
                try:
                    parent = await element.query_selector("..")
                    if parent:
                        parent_classes = await parent.get_attribute("class") or ""
                except:
                    pass
                
                input_details.append({
                    "index": i,
                    "tag": tag,
                    "type": input_type,
                    "placeholder": placeholder,
                    "name": name,
                    "id": element_id,
                    "class": class_attr,
                    "aria-label": aria_label,
                    "parent_classes": parent_classes
                })
            except Exception as e:
                print(f"Error collecting details for input {i}: {e}")
                continue
        
        # Collect detailed information about each button element
        for i, element in enumerate(button_elements):
            try:
                text = await element.inner_text() or ""
                element_id = await element.get_attribute("id") or ""
                class_attr = await element.get_attribute("class") or ""
                aria_label = await element.get_attribute("aria-label") or ""
                
                # Get closest parent classes
                parent_classes = ""
                try:
                    parent = await element.query_selector("..")
                    if parent:
                        parent_classes = await parent.get_attribute("class") or ""
                except:
                    pass
                
                button_details.append({
                    "index": i,
                    "text": text.strip(),
                    "id": element_id,
                    "class": class_attr,
                    "aria-label": aria_label,
                    "parent_classes": parent_classes
                })
            except Exception as e:
                print(f"Error collecting details for button {i}: {e}")
                continue
        
        # Print inspection results
        print("\n=== INPUT ELEMENTS FOUND ===")
        for detail in input_details:
            print(f"Input #{detail['index']}:")
            print(f"  Tag: {detail['tag']}")
            print(f"  Type: {detail['type']}")
            print(f"  Placeholder: '{detail['placeholder']}'")
            print(f"  Name: '{detail['name']}'")
            print(f"  ID: '{detail['id']}'")
            print(f"  Class: '{detail['class']}'")
            print(f"  Aria-label: '{detail['aria-label']}'")
            print(f"  Parent classes: '{detail['parent_classes']}'")
            print()
        
        print("\n=== BUTTON ELEMENTS FOUND ===")
        for detail in button_details:
            print(f"Button #{detail['index']}:")
            print(f"  Text: '{detail['text']}'")
            print(f"  ID: '{detail['id']}'")
            print(f"  Class: '{detail['class']}'")
            print(f"  Aria-label: '{detail['aria-label']}'")
            print(f"  Parent classes: '{detail['parent_classes']}'")
            print()
        
        # Look for specific coupon-related elements by inspecting the collected data
        results = {
            "coupon_input": None,
            "apply_button": None,
            "open_button": None,
            "all_inputs": input_details,
            "all_buttons": button_details
        }
        
        # Search for potential coupon controls in the collected data
        print("Searching for potential coupon controls...")
        
        # Look for inputs that might be coupon fields (without hardcoding placeholder text)
        for input_detail in input_details:
            if input_detail["type"] == "text" and ("kod" in input_detail["placeholder"].lower() or 
                                                  "indirim" in input_detail["placeholder"].lower()):
                print("Found potential coupon input field")
                results["coupon_input"] = input_detail
                break
        
        # Look for buttons with common coupon action text
        for button_detail in button_details:
            if ("kodu gir" in button_detail["text"].lower() or 
                "uygula" in button_detail["text"].lower() or
                "kupon" in button_detail["text"].lower()):
                print("Found potential coupon control button")
                # If it's a "Kodu Gir" button, it might open the coupon area
                if "kodu gir" in button_detail["text"].lower():
                    results["open_button"] = button_detail
                elif "uygula" in button_detail["text"].lower() or "kupon" in button_detail["text"].lower():
                    results["apply_button"] = button_detail
        
        # Print final analysis
        print("\n=== COUPON ANALYSIS ===")
        print(f"Coupon input found: {'YES' if results['coupon_input'] else 'NO'}")
        if results["coupon_input"]:
            print(f"  Type: {results['coupon_input']['type']}")
            print(f"  Placeholder: '{results['coupon_input']['placeholder']}'")
        
        print(f"Apply button found: {'YES' if results['apply_button'] else 'NO'}")
        if results["apply_button"]:
            print(f"  Text: '{results['apply_button']['text']}'")
        
        print(f"Open button found: {'YES' if results['open_button'] else 'NO'}")
        if results["open_button"]:
            print(f"  Text: '{results['open_button']['text']}'")
        
        # Export to JSON file
        os.makedirs("artifacts", exist_ok=True)
        # Write with explicit UTF-8 encoding to avoid issues
        temp_file = "artifacts/trendyol_coupon_controls.json.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        # Rename temp file to final file name to ensure atomic write
        os.replace(temp_file, "artifacts/trendyol_coupon_controls.json")
        
        print("\nResults exported to artifacts/trendyol_coupon_controls.json")
        
        # Take screenshot
        await page.screenshot(path="artifacts/trendyol_coupon_inspection.png", full_page=True)
        print("Screenshot saved as artifacts/trendyol_coupon_inspection.png")
        
        # Keep browser open for manual inspection
        print("\nBrowser is now open. Please inspect the elements and press Enter to close...")
        input()
        
    except Exception as e:
        print(f"Error during inspection: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # The browser will be closed by the BrowserManager's lifecycle management
        print("Browser cleanup completed")

if __name__ == "__main__":
    asyncio.run(inspect_trendyol_coupon_page())
