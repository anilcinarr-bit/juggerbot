import logging
from typing import Dict, Any
from playwright.async_api import Page, TimeoutError

from app.adapters.base import BaseAdapter
from app.browser.browser_manager import BrowserManager
from app.platforms.hepsiburada import HOME_URL, CHECKOUT_URL, COUPON_INPUT_SELECTOR, APPLY_BUTTON_SELECTOR, RESULT_SELECTOR
from app.models.coupon_result import classify_hepsiburada_result, CouponStatus

logger = logging.getLogger("adapters.hepsiburada")


class HepsiburadaAdapter(BaseAdapter):
    """Hepsiburada coupon redemption adapter"""
    
    async def execute(self, coupon: str) -> Dict[str, Any]:
        """Execute the Hepsiburada coupon redemption automation"""
        logger.info(f"Executing Hepsiburada automation for coupon: {coupon}")
        
        try:
            # Get browser manager instance
            browser_manager = BrowserManager()
            
            # Ensure browser is available
            if not browser_manager.available:
                await browser_manager.start()
            
            # Create a new page from the persistent context (this is the key fix)
            page = await browser_manager.new_page()
            
            # Navigate directly to the cart page for coupon redemption
            logger.info("Navigating to Hepsiburada cart")
            await page.goto("https://checkout.hepsiburada.com/sepetim", wait_until="domcontentloaded", timeout=30000)
            logger.info("Hepsiburada cart loaded")
            
            # Find and click the "Kupon kodu ekle" control
            logger.info("Opening coupon drawer")
            try:
                # Try the preferred locator first
                await page.get_by_label("Kupon kodu ekle").click(timeout=10000)
            except TimeoutError:
                # Fallback to text-based locator if needed
                await page.get_by_text("Kupon kodu ekle", exact=True).click(timeout=10000)
            logger.info("Coupon drawer opened")
            
            # Find visible coupon input directly (without relying on BasketCoupons container)
            logger.info("Finding visible coupon input")
            coupon_inputs = page.get_by_placeholder("Kupon kodunuzu girin")
            visible_coupon_inputs = await coupon_inputs.all()  # Get all matching elements
            
            # Log diagnostic information
            total_inputs = len(visible_coupon_inputs)
            visible_count = sum([await inp.is_visible() for inp in visible_coupon_inputs])
            logger.info(f"Total coupon inputs found: {total_inputs}")
            logger.info(f"Visible coupon inputs found: {visible_count}")
            
            # Find the first visible input
            visible_input = None
            for inp in visible_coupon_inputs:
                is_visible = await inp.is_visible()
                if is_visible:
                    visible_input = inp
                    break
            
            if not visible_input:
                # If no visible input found, wait for one to appear
                try:
                    # Wait for at least one coupon input to be visible
                    await page.wait_for_selector('input[placeholder="Kupon kodunuzu girin"]', state='visible', timeout=10000)
                    # Get the first visible one now
                    visible_coupon_inputs = await page.get_by_placeholder("Kupon kodunuzu girin").all()
                    visible_count = sum([await inp.is_visible() for inp in visible_coupon_inputs])
                    logger.info(f"Total coupon inputs found after wait: {len(visible_coupon_inputs)}")
                    logger.info(f"Visible coupon inputs found after wait: {visible_count}")
                    for inp in visible_coupon_inputs:
                        if await inp.is_visible():
                            visible_input = inp
                            break
                except TimeoutError:
                    logger.error("No visible coupon input found after waiting")
                    raise
            
            if not visible_input:
                logger.error("No visible coupon input found")
                return {
                    "success": False,
                    "message": "Coupon input not found",
                    "coupon": coupon,
                    "status": "error"
                }
            
            logger.info("Coupon input found")
            
            # Fill the coupon code
            await visible_input.fill(coupon)
            logger.info("Coupon code filled")
            
            # Find the "Ekle" button associated with this visible input
            # We'll locate it by finding all Ekle buttons and then checking which one is visible and related to the input
            logger.info("Finding associated 'Ekle' button")
            ekle_buttons = page.get_by_role("button", name="Ekle", exact=True)
            visible_ekle_buttons = await ekle_buttons.all()
            
            # Log diagnostic information for buttons
            total_buttons = len(visible_ekle_buttons)
            visible_button_count = sum([await btn.is_visible() for btn in visible_ekle_buttons])
            logger.info(f"Total exact Ekle buttons found: {total_buttons}")
            logger.info(f"Visible exact Ekle buttons found: {visible_button_count}")
            
            # Try to find the button associated with this specific input
            add_button = None
            
            # If there's exactly one visible button, use it
            if visible_button_count == 1:
                for btn in visible_ekle_buttons:
                    if await btn.is_visible():
                        add_button = btn
                        break
            elif visible_button_count > 1:
                # Try to find a DOM relationship between input and buttons
                try:
                    # Get the parent container of the coupon input
                    input_parent = await visible_input.locator('xpath=..').first
                    if input_parent:
                        # Look for Ekle buttons within this parent
                        parent_ekle_buttons = input_parent.get_by_role("button", name="Ekle", exact=True)
                        parent_visible_buttons = await parent_ekle_buttons.all()
                        
                        # Check which of these are visible
                        for btn in parent_visible_buttons:
                            if await btn.is_visible():
                                add_button = btn
                                break
                except Exception as e:
                    logger.debug(f"Could not establish DOM relationship: {e}")
                
                # If we still haven't found a button, it's ambiguous - return error
                if not add_button:
                    logger.error("Multiple visible Ekle buttons found but no clear DOM relationship to input")
                    return {
                        "success": False,
                        "message": "Ambiguous Ekle button selection",
                        "coupon": coupon,
                        "status": "error"
                    }
            else:
                # No visible buttons found
                logger.error("No visible 'Ekle' button found")
                return {
                    "success": False,
                    "message": "Add button not found",
                    "coupon": coupon,
                    "status": "error"
                }
            
            # Wait for the "Ekle" button to become enabled
            # Use polling approach since wait_for with "enabled" state is not supported
            import asyncio
            start_time = asyncio.get_event_loop().time()
            timeout_seconds = 10
            button_enabled = False
            
            while not button_enabled and (asyncio.get_event_loop().time() - start_time) < timeout_seconds:
                try:
                    button_enabled = await add_button.is_enabled()
                    if not button_enabled:
                        # Wait a short time before checking again
                        await asyncio.sleep(0.1)
                except Exception as e:
                    logger.debug(f"Error checking button enabled state: {e}")
                    # If there's an error checking, continue trying
                    await asyncio.sleep(0.1)
            
            if not button_enabled:
                logger.error("Ekle button did not become enabled within 10 seconds")
                return {
                    "success": False,
                    "message": "Ekle button did not become enabled",
                    "coupon": coupon,
                    "status": "error"
                }
                
            logger.info("Add button enabled")
            
            # Click the "Ekle" button
            await add_button.click()
            logger.info("Coupon submitted")
            
            # Wait for Hepsiburada result toast
            logger.info("Waiting for Hepsiburada coupon result")
            try:
                # Use Playwright's wait_for with visible timeout to detect toast
                toast = page.locator('.hb-toast-notifier-container').first
                await toast.wait_for(timeout=5000)  # Wait up to 5 seconds for toast
                
                if await toast.is_visible():
                    toast_text = await toast.inner_text()
                    logger.info(f"Hepsiburada coupon result: {toast_text}")
                    
                    # Normalize text for classification (lowercase, trim whitespace)
                    normalized_text = toast_text.strip().lower()
                    
                    # Check for verified invalid response
                    if "geçersiz bir kod girdin" in normalized_text:
                        logger.info("Coupon result classified as invalid")
                        return {
                            "success": False,
                            "message": toast_text,
                            "coupon": coupon,
                            "status": "invalid"
                        }
                    else:
                        # Unrecognized toast result - classify it using our new system
                        logger.info("Unrecognized Hepsiburada coupon result; classifying with new system")
                        classified_status = classify_hepsiburada_result(toast_text)
                        logger.info(f"[Hepsiburada] Raw result: \"{toast_text}\"")
                        logger.info(f"[Hepsiburada] Classification: {classified_status.value}")
                        
                        # Return the properly classified result
                        if classified_status == CouponStatus.SUCCESS:
                            return {
                                "success": True,
                                "message": toast_text,
                                "coupon": coupon,
                                "status": "success"
                            }
                        elif classified_status in [CouponStatus.INVALID, CouponStatus.ALREADY_USED, 
                                                  CouponStatus.EXPIRED, CouponStatus.MIN_CART]:
                            return {
                                "success": False,
                                "message": toast_text,
                                "coupon": coupon,
                                "status": classified_status.value.lower()
                            }
                        else:
                            # For unknown cases, return UNKNOWN status
                            logger.info("Unknown classification result; returning UNKNOWN")
                            return {
                                "success": False,
                                "message": toast_text,
                                "coupon": coupon,
                                "status": "unknown"
                            }
                else:
                    # Toast exists but is not visible - treat as no result detected
                    logger.info("No recognized Hepsiburada result detected after submission")
                    # Return UNKNOWN status for cases with no visible message
                    return {
                        "success": False,
                        "message": "No visible message after submission",
                        "coupon": coupon,
                        "status": "unknown"
                    }
                    
            except Exception:
                # No toast appeared within timeout - treat as no result detected
                logger.info("No recognized Hepsiburada result detected after submission")
                # Return UNKNOWN status for cases with no visible message
                return {
                    "success": False,
                    "message": "No visible message after submission",
                    "coupon": coupon,
                    "status": "unknown"
                }
                
        except Exception as e:
            logger.error(f"Error in Hepsiburada automation: {e}")
            return {
                "success": False,
                "message": f"Error during automation: {str(e)}",
                "coupon": coupon,
                "status": "error"
            }



