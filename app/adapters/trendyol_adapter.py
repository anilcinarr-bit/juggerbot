import logging
from typing import Dict, Any
from playwright.async_api import Page, TimeoutError
import os

from app.adapters.base import BaseAdapter
from app.browser.browser_manager import BrowserManager
from app.platforms.trendyol import CART_URL, COUPON_INPUT_SELECTOR, APPLY_BUTTON_SELECTOR

logger = logging.getLogger("adapters.trendyol")


class TrendyolAdapter(BaseAdapter):
    """Trendyol coupon redemption adapter"""
    
    async def execute(self, coupon: str) -> Dict[str, Any]:
        """Execute the Trendyol coupon redemption automation"""
        logger.info(f"Executing Trendyol automation for coupon: {coupon}")
        
        try:
            # Get browser manager instance
            browser_manager = BrowserManager()
            
            # Ensure browser is available
            if not browser_manager.available:
                await browser_manager.start()
            
            # Create a new page from the persistent context (this is the key fix)
            page = await browser_manager.new_page()
            
            # Navigate directly to cart page for coupon redemption
            logger.info("Navigating to Trendyol cart")
            await page.goto(CART_URL, wait_until="networkidle", timeout=30000)
            logger.info("Trendyol cart loaded")
            
            # Wait for cart to be fully loaded (React content loaded)
            await page.wait_for_load_state("networkidle")
            
            # Click the coupon open button
            logger.info("Clicking coupon open button")
            try:
                # Use the confirmed selector for the open button
                open_button = page.locator(".use-promotion-code-button")
                await open_button.click()
                logger.info("Coupon open button clicked")
            except Exception as e:
                logger.error(f"Error clicking coupon open button: {e}")
                return {
                    "success": False,
                    "message": f"Error clicking coupon open button: {str(e)}",
                    "coupon": coupon,
                    "status": "error"
                }
            
            # Wait for coupon input to become visible using the placeholder locator
            logger.info("Waiting for coupon input to become visible")
            try:
                # Use the placeholder locator as specified in the DOM
                coupon_input = await page.wait_for_selector(
                    'input[placeholder="İndirim Kodu Gir"]',
                    state="visible",
                    timeout=10000
                )
                logger.info("Coupon input found")
            except TimeoutError:
                logger.error("Coupon input did not become visible after clicking button")
                return {
                    "success": False,
                    "message": "Coupon input not visible after clicking button",
                    "coupon": coupon,
                    "status": "error"
                }
            
            # Fill the coupon code
            logger.info(f"Entering coupon code: {coupon}")
            await page.fill('input[placeholder="İndirim Kodu Gir"]', coupon)
            logger.info("Coupon filled")
            
            # Verify the input value matches the coupon (as requested)
            logger.info("Verifying coupon value")
            input_value = await page.input_value('input[placeholder="İndirim Kodu Gir"]')
            if input_value != coupon:
                logger.warning(f"Coupon value mismatch: expected {coupon}, got {input_value}")
                # This is not necessarily an error, but we log it for debugging
            else:
                logger.info("Coupon value verified")
            
            # Wait for apply button to become enabled (the "disabled" class disappears)
            logger.info("Waiting for apply button to become enabled")
            try:
                apply_button = page.locator(".promotion-code-button")
                # Poll until the button is not disabled
                import asyncio
                start_time = asyncio.get_event_loop().time()
                timeout_seconds = 10
                button_enabled = False
                
                while not button_enabled and (asyncio.get_event_loop().time() - start_time) < timeout_seconds:
                    try:
                        # Check if the "disabled" class is present on the button
                        disabled_class = await apply_button.first.get_attribute("class")
                        if disabled_class and "disabled" in disabled_class:
                            logger.debug("Apply button still disabled, waiting...")
                            await asyncio.sleep(0.2)
                        else:
                            logger.info("Apply button enabled")
                            button_enabled = True
                    except Exception as e:
                        logger.debug(f"Error checking button state: {e}")
                        await asyncio.sleep(0.2)
                
                if not button_enabled:
                    logger.error("Apply button did not become enabled within 10 seconds")
                    return {
                        "success": False,
                        "message": "Apply button did not become enabled",
                        "coupon": coupon,
                        "status": "error"
                    }
            except Exception as e:
                logger.error(f"Error waiting for apply button to enable: {e}")
                return {
                    "success": False,
                    "message": f"Error waiting for apply button: {str(e)}",
                    "coupon": coupon,
                    "status": "error"
                }
            
            # Click the apply button
            logger.info("Clicking apply button")
            await apply_button.first.click()
            logger.info("Apply clicked")
            
            # Wait for result to appear
            logger.info("Waiting for Trendyol coupon result")
            await page.wait_for_timeout(2000)  # Give time for the result to show
            
            # Get the text content of the apply button after submission to determine result
            try:
                button_text = await apply_button.first.inner_text()
                if button_text and "uygula" in button_text.lower():
                    logger.info("Coupon submitted successfully (apply button text unchanged)")
                    return {
                        "success": True,
                        "message": "Coupon submitted for processing",
                        "coupon": coupon,
                        "status": "submitted_unverified"
                    }
                else:
                    # The button text changed, which indicates success or error
                    logger.info(f"Coupon result: {button_text.strip()}")
                    return {
                        "success": True,
                        "message": button_text.strip(),
                        "coupon": coupon,
                        "status": "success"  # Default to success for now, but this should be refined based on content
                    }
            except Exception as e:
                logger.warning(f"Could not get button text after submission: {e}")
                # Try alternative approach to detect result by checking for error messages in page context
                try:
                    # Look for common error message selectors that might appear
                    error_selectors = [
                        ".coupon-error-message",  # Custom selector for errors
                        ".error-message",         # General error messages
                        ".alert-danger",          # Bootstrap style danger alerts
                        "[class*='error']",       # Any element with error in class name
                        ".toast-container"        # Toast notifications (often used for messages)
                    ]
                    error_found = False
                    for selector in error_selectors:
                        try:
                            error_element = page.locator(selector)
                            elements = await error_element.all()
                            if elements and len(elements) > 0:
                                for element in elements:
                                    if await element.is_visible():
                                        error_text = await element.inner_text()
                                        if error_text.strip():
                                            logger.info(f"Error message found: {error_text.strip()}")
                                            # Classify based on content
                                            normalized_text = error_text.strip().lower()
                                            if "geçersiz" in normalized_text or "invalid" in normalized_text or \
                                               "kupon kodu geçersiz" in normalized_text:
                                                return {
                                                    "success": False,
                                                    "message": error_text.strip(),
                                                    "coupon": coupon,
                                                    "status": "invalid"
                                                }
                                            elif "süresi dolmuş" in normalized_text or "expired" in normalized_text:
                                                return {
                                                    "success": False,
                                                    "message": error_text.strip(),
                                                    "coupon": coupon,
                                                    "status": "expired"
                                                }
                                            elif "kullanılmış" in normalized_text or "already used" in normalized_text:
                                                return {
                                                    "success": False,
                                                    "message": error_text.strip(),
                                                    "coupon": coupon,
                                                    "status": "already_used"
                                                }
                                            elif "minimum" in normalized_text or "minumum" in normalized_text:
                                                return {
                                                    "success": False,
                                                    "message": error_text.strip(),
                                                    "coupon": coupon,
                                                    "status": "minimum_cart"
                                                }
                                            else:
                                                # General error case
                                                return {
                                                    "success": False,
                                                    "message": error_text.strip(),
                                                    "coupon": coupon,
                                                    "status": "error"
                                                }
                        except Exception:
                            continue
                    # If no error found, assume success since we submitted without errors
                    logger.info("No specific error message detected, assuming submission was successful")
                    return {
                        "success": True,
                        "message": "Coupon submitted for processing",
                        "coupon": coupon,
                        "status": "submitted_unverified"
                    }
                except Exception as e2:
                    logger.error(f"Failed to determine result after submission: {e2}")
                    return {
                        "success": False,
                        "message": f"Error determining result: {str(e2)}",
                        "coupon": coupon,
                        "status": "error"
                    }

        except Exception as e:
            logger.error(f"Error in Trendyol automation: {e}")
            return {
                "success": False,
                "message": f"Error during automation: {str(e)}",
                "coupon": coupon,
                "status": "error"
            }


