import sys
from pathlib import Path

# Add project root to path so we can import from app.*
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
import os
import json
from playwright.async_api import async_playwright, Page
from app.browser.browser_manager import BrowserManager

# Test coupon to use for inspection
TEST_COUPON = "HEPSI-500"

async def capture_dom_snapshot(page: Page):
    """Capture a structured DOM snapshot"""
    try:
        # Get focused element information
        elements_info = []
        
        # Get all elements with common result-related attributes
        selector_list = [
            '[role="alert"]',
            '[role="status"]', 
            '[aria-live]',
            '[data-testid]',
            '[class*="coupon"]',
            '[class*="message"]',
            '[class*="toast"]',
            '[class*="notification"]',
            '[class*="error"]',
            '[class*="success"]',
            '[class*="valid"]',
            '[class*="invalid"]',
            '[id*="coupon"]',
            '[id*="message"]',
            '[id*="toast"]'
        ]
        
        for selector in selector_list:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    try:
                        # Get actual tag name using JavaScript evaluation
                        tag_name = await page.evaluate('element => element.tagName.toLowerCase()', element)
                        
                        element_info = {
                            'selector': selector,
                            'tag': tag_name,
                            'id': await element.get_attribute('id'),
                            'class': await element.get_attribute('class'),
                            'role': await element.get_attribute('role'),
                            'aria_label': await element.get_attribute('aria-label'),
                            'aria_live': await element.get_attribute('aria-live'),
                            'data_testid': await element.get_attribute('data-testid'),
                            'placeholder': await element.get_attribute('placeholder'),
                            'text': (await element.inner_text())[:300] if await element.is_visible() else '',
                            'visible': await element.is_visible(),
                            'is_enabled': await element.is_enabled() if hasattr(element, 'is_enabled') else None
                        }
                        # Filter out empty/None values
                        element_info = {k: v for k, v in element_info.items() if v is not None and v != ''}
                        elements_info.append(element_info)
                    except Exception:
                        continue
            except Exception:
                continue
                
        return elements_info
    except Exception as e:
        print(f"Error capturing DOM snapshot: {e}")
        return []

async def create_inspection_script():
    """Create the inspection script"""
    
    # Ensure artifacts directory exists
    os.makedirs('artifacts', exist_ok=True)
    
    # Get BrowserManager instance
    browser_manager = BrowserManager()
    
    # Check if browser is available, start if needed
    if not browser_manager.available:
        await browser_manager.start()
    
    # Create a new page from the persistent context
    page = await browser_manager.new_page()
    
    try:
        print("=== Hepsiburada Coupon Result Inspection ===")
        print(f"Coupon: {TEST_COUPON}")
        
        # Navigate to cart page
        print("Navigating to cart...")
        await page.goto("https://checkout.hepsiburada.com/sepetim", wait_until="domcontentloaded", timeout=30000)
        print("Cart loaded")
        
        # Find and click "Kupon kodu ekle"
        print("Opening coupon UI...")
        try:
            await page.get_by_label("Kupon kodu ekle").click(timeout=10000)
        except Exception:
            await page.get_by_text("Kupon kodu ekle", exact=True).click(timeout=10000)
        print("Coupon UI opened")
        
        # Find visible coupon input
        print("Finding visible coupon input...")
        coupon_inputs = page.get_by_placeholder("Kupon kodunuzu girin")
        visible_coupon_inputs = await coupon_inputs.all()
        
        # Wait for at least one visible input to appear (with timeout)
        visible_input = None
        for i in range(10):  # Try 10 times with 0.5s intervals
            visible_coupon_inputs = await coupon_inputs.all()
            for inp in visible_coupon_inputs:
                if await inp.is_visible():
                    visible_input = inp
                    break
            if visible_input:
                break
            await asyncio.sleep(0.5)
            
        if not visible_input:
            print("No visible coupon input found")
            return
            
        print("Coupon input found")
        
        # Fill the coupon code
        print(f"Filling coupon: {TEST_COUPON}")
        await visible_input.fill(TEST_COUPON)
        print("Coupon filled")
        
        # Find the "Ekle" button
        print("Finding Ekle button...")
        ekle_buttons = page.get_by_role("button", name="Ekle", exact=True)
        visible_ekle_buttons = await ekle_buttons.all()
        
        add_button = None
        if len(visible_ekle_buttons) == 1:
            add_button = visible_ekle_buttons[0]
        elif len(visible_ekle_buttons) > 1:
            # Try to find the button associated with this specific input
            try:
                input_parent = await visible_input.locator('xpath=..').first
                if input_parent:
                    parent_ekle_buttons = input_parent.get_by_role("button", name="Ekle", exact=True)
                    parent_visible_buttons = await parent_ekle_buttons.all()
                    for btn in parent_visible_buttons:
                        if await btn.is_visible():
                            add_button = btn
                            break
            except Exception as e:
                print(f"Could not establish DOM relationship: {e}")
        
        if not add_button:
            # If we still haven't found a button, use the first visible one
            for btn in visible_ekle_buttons:
                if await btn.is_visible():
                    add_button = btn
                    break
                    
        if not add_button:
            print("No Ekle button found")
            return
            
        print("Ekle button found")
        
        # Wait for button to become enabled using polling approach (not wait_for with "enabled")
        print("Waiting for Ekle button to become enabled...")
        start_time = asyncio.get_event_loop().time()
        timeout_seconds = 10
        button_enabled = False
        
        while not button_enabled and (asyncio.get_event_loop().time() - start_time) < timeout_seconds:
            try:
                button_enabled = await add_button.is_enabled()
                if not button_enabled:
                    await asyncio.sleep(0.1)
            except Exception as e:
                print(f"Error checking button enabled state: {e}")
                await asyncio.sleep(0.1)
        
        if not button_enabled:
            print("Ekle button did not become enabled within 10 seconds")
            return
            
        print("Ekle button enabled")
        
        # Before submission - capture DOM snapshot
        print("Capturing pre-submission DOM...")
        before_snapshot = await capture_dom_snapshot(page)
        
        # Save the HTML before submission
        before_html = await page.content()
        with open('artifacts/hepsiburada_result_before.html', 'w', encoding='utf-8') as f:
            f.write(before_html)
            
        with open('artifacts/hepsiburada_result_before.json', 'w', encoding='utf-8') as f:
            json.dump(before_snapshot, f, indent=2, ensure_ascii=False)
        
        # Install MutationObserver
        print("Installing MutationObserver...")
        await page.evaluate("""
            window.mutationObserverRecords = [];
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'childList' || mutation.type === 'attributes') {
                        window.mutationObserverRecords.push({
                            type: mutation.type,
                            timestamp: Date.now(),
                            target: {
                                tagName: mutation.target.tagName,
                                id: mutation.target.id,
                                className: mutation.target.className
                            },
                            addedNodes: Array.from(mutation.addedNodes).map(node => ({
                                tagName: node.tagName,
                                id: node.id,
                                className: node.className,
                                textContent: node.textContent ? node.textContent.substring(0, 300) : ''
                            })),
                            removedNodes: Array.from(mutation.removedNodes).map(node => ({
                                tagName: node.tagName,
                                id: node.id,
                                className: node.className,
                                textContent: node.textContent ? node.textContent.substring(0, 300) : ''
                            })),
                            attributeName: mutation.attributeName
                        });
                    }
                });
            });
            observer.observe(document.body, { 
                childList: true, 
                subtree: true,
                attributes: true,
                attributeFilter: ['class', 'style', 'aria-live', 'role']
            });
        """)
        
        print("Installing MutationObserver... [Done]")
        
        # Submit the coupon
        print("Submitting coupon...")
        await add_button.click()
        print("Coupon submitted")
        
        # Observe result UI for approximately 5 seconds after submission
        # This allows capturing of delayed or temporary notifications
        print("Observing result UI for full 5 seconds...")
        start_time = asyncio.get_event_loop().time()
        observation_duration = 5  # seconds
        
        # Track candidates seen during the entire observation period
        all_observed_candidates = []
        seen_element_ids = set()  # To avoid duplicate entries
        
        while (asyncio.get_event_loop().time() - start_time) < observation_duration:
            # Periodically check for result-like elements during the observation window
            after_snapshot = await capture_dom_snapshot(page)
            
            # Search for result candidates in current DOM
            result_terms = ['kupon', 'geçersiz', 'gecersiz', 'başarılı', 'basarili', 'eklendi', 'uygulan', 
                           'kullanılmış', 'kullanilmis', 'kullanıldı', 'kullanildi', 'süresi', 'suresi', 
                           'doldu', 'minimum', 'sepet', 'uygun', 'hata', 'error', 'invalid', 'success']
            
            # Only use result-specific terms for strong candidates (not generic "kupon")
            strong_result_terms = ['geçersiz', 'gecersiz', 'başarılı', 'basarili', 'eklendi', 'uygulan', 
                                  'kullanılmış', 'kullanilmis', 'kullanıldı', 'kullanildi', 'süresi doldu', 
                                  'suresi doldu', 'uygun değil', 'uygun degil', 'hata', 'error', 'invalid', 'success']
            
            # Find candidates in current snapshot
            current_candidates = []
            for element in after_snapshot:
                text = element.get('text', '').lower()
                
                # Check if this is a new element (not seen before)
                element_id = f"{element.get('tag', '')}_{element.get('id', '')}_{element.get('class', '')}"
                is_new_element = element_id not in seen_element_ids
                
                if is_new_element:
                    seen_element_ids.add(element_id)
                
                # Check for strong result indicators
                strong_match = any(term in text for term in strong_result_terms)
                semantic_match = (element.get('role', '').lower() in ['alert', 'status'] or 
                                 'live' in element.get('aria_live', '').lower())
                
                if strong_match or semantic_match:
                    # Add source information to distinguish between new and existing elements
                    candidate_with_source = {
                        **element,
                        'source': 'new_element' if is_new_element else 'existing_element',
                        'strong_match': strong_match,
                        'semantic_match': semantic_match
                    }
                    current_candidates.append(candidate_with_source)
            
            # Add to accumulated candidates
            all_observed_candidates.extend(current_candidates)
            
            # Wait before next check
            await asyncio.sleep(0.2)
        
        print("Observation completed")
        
        # Capture final DOM after observation window
        print("Capturing post-submission DOM...")
        after_snapshot = await capture_dom_snapshot(page)
        
        # Save the HTML after submission
        after_html = await page.content()
        with open('artifacts/hepsiburada_result_after.html', 'w', encoding='utf-8') as f:
            f.write(after_html)
            
        with open('artifacts/hepsiburada_result_after.json', 'w', encoding='utf-8') as f:
            json.dump(after_snapshot, f, indent=2, ensure_ascii=False)
        
        # Get MutationObserver records
        try:
            mutation_records = await page.evaluate("window.mutationObserverRecords")
            with open('artifacts/hepsiburada_result_mutations.json', 'w', encoding='utf-8') as f:
                json.dump(mutation_records, f, indent=2, ensure_ascii=False)
            print(f"Mutation records captured: {len(mutation_records)}")
        except Exception as e:
            print(f"Error getting mutation records: {e}")
            mutation_records = []
        
        # Prioritize candidates based on source and strength of evidence
        # Group by source type for ranking
        new_strong_candidates = [c for c in all_observed_candidates if c.get('strong_match') and c.get('source') == 'new_element']
        new_semantic_candidates = [c for c in all_observed_candidates if c.get('semantic_match') and c.get('source') == 'new_element']
        changed_strong_candidates = [c for c in all_observed_candidates if c.get('strong_match') and c.get('source') == 'existing_element']
        changed_semantic_candidates = [c for c in all_observed_candidates if c.get('semantic_match') and c.get('source') == 'existing_element']
        
        # Combine candidates in priority order
        strong_result_candidates = []
        strong_result_candidates.extend(new_strong_candidates)
        strong_result_candidates.extend(new_semantic_candidates)
        strong_result_candidates.extend(changed_strong_candidates)
        strong_result_candidates.extend(changed_semantic_candidates)
        
        # Remove duplicates while preserving order
        seen_candidate_ids = set()
        unique_strong_candidates = []
        for candidate in strong_result_candidates:
            # Create a simple identifier for deduplication (based on key attributes)
            candidate_id = f"{candidate.get('tag', '')}_{candidate.get('id', '')}_{candidate.get('text', '')[:50]}"
            if candidate_id not in seen_candidate_ids:
                seen_candidate_ids.add(candidate_id)
                unique_strong_candidates.append(candidate)
        
        strong_result_candidates = unique_strong_candidates
        
        # Save all candidates (not just final snapshot)
        with open('artifacts/hepsiburada_result_candidates.json', 'w', encoding='utf-8') as f:
            json.dump(all_observed_candidates, f, indent=2, ensure_ascii=False)
        
        print(f"Mutation records captured: {len(mutation_records)}")
        print(f"Transient candidates captured: {len(all_observed_candidates)}")
        print(f"Strong result candidates: {len(strong_result_candidates)}")
        
        # Print summary of strongest candidates (after full observation)
        if strong_result_candidates:
            print("\n=== Strongest Result Candidates ===")
            for i, candidate in enumerate(strong_result_candidates[:5]):  # Show first 5
                print(f"\nCandidate {i+1}:")
                print(f"  Source: {candidate.get('source', 'N/A')}")
                print(f"  Tag: {candidate.get('tag', 'N/A')}")
                print(f"  Role: {candidate.get('role', 'N/A')}")
                print(f"  Aria-live: {candidate.get('aria_live', 'N/A')}")
                print(f"  Data-testid: {candidate.get('data_testid', 'N/A')}")
                print(f"  ID: {candidate.get('id', 'N/A')}")
                print(f"  Class: {candidate.get('class', 'N/A')}")
                print(f"  Text: {candidate.get('text', 'N/A')[:200]}...")
        else:
            print("\nNo strong result candidates identified during observation period")
        
        print("\n=== Inspection Complete ===")
        print("Artifacts saved in artifacts/ directory")
        
    except Exception as e:
        print(f"Error during inspection: {e}")
        raise
    finally:
        # Safely close the page without closing the browser context
        try:
            await page.close()
        except Exception:
            pass

async def main():
    await create_inspection_script()

if __name__ == "__main__":
    asyncio.run(main())