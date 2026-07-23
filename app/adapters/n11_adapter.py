import logging
from typing import Dict, Any
from playwright.async_api import Page, TimeoutError

from app.adapters.base import BaseAdapter
from app.browser.browser_manager import BrowserManager
from app.platforms.n11 import CART_URL
from app.models.coupon_result import classify_result, CouponStatus

logger = logging.getLogger("adapters.n11")


class N11Adapter(BaseAdapter):
    """N11 coupon redemption adapter"""
    
    async def _validate_n11_cart_page(self, page: Page) -> bool:
        """Validate that the loaded page is actually the N11 cart page and not a Cloudflare/server error"""
        try:
            # Get page title
            title = await page.title()
            
            # Check for common error patterns in title
            if "504" in title.lower() or "gateway time-out" in title.lower():
                logger.warning("[N11] Gateway timeout detected")
                return False
            elif "503" in title.lower() or "service unavailable" in title.lower():
                logger.warning("[N11] Service Unavailable detected")
                return False
            elif "502" in title.lower() or "bad gateway" in title.lower():
                logger.warning("[N11] Error 502 detected")
                return False
            elif "cloudflare" in title.lower():
                logger.warning("[N11] Cloudflare page detected")
                return False
            elif "host error" in title.lower():
                logger.warning("[N11] Host error detected")
                return False
            elif "maintenance" in title.lower():
                logger.warning("[N11] Maintenance page detected")
                return False
            
            # Skip page.content() serialization on SPA pages.
            expected_elements = [
                ".cartCouponWrapper",  # Main cart wrapper
                "button:has-text('Kuponlarım')",  # Coupon button text
                "input.coupons-main-input"  # Coupon input field
            ]
            
            for element_selector in expected_elements:
                try:
                    element = await page.query_selector(element_selector)
                    if element and await element.is_visible():
                        return True  # Found a valid cart element
                except Exception:
                    continue
            
            # If we got here, we didn't find any valid cart elements
            logger.warning("[N11] Application unavailable page detected")
            return False
            
        except Exception as e:
            logger.error(f"[N11] Error validating page: {e}")
            return False
    
    async def execute(self, coupon: str) -> Dict[str, Any]:
        """Execute the N11 coupon redemption automation"""
        logger.info(f"Executing N11 automation for coupon: {coupon}")
        
        try:
            # Get browser manager instance
            browser_manager = BrowserManager()
            
            # Create a new page from the persistent context (this is the key fix)
            page = await browser_manager.new_page()
            
            # Navigate directly to cart page for coupon redemption
            logger.info("Navigating to N11 cart")
            
            # Retry mechanism for Cloudflare/server errors
            max_retries = 3
            retry_count = 0
            page_loaded = False
            
            while not page_loaded and retry_count < max_retries:
                try:
                    await page.goto(CART_URL, wait_until="domcontentloaded", timeout=30000)
                    logger.info("N11 cart loaded")
                    
                    # Add diagnostic logging immediately after navigation
                    try:
                        diagnostics = await page.evaluate("""
                            () => {
                                return {
                                    href: location.href,
                                    innerWidth: window.innerWidth,
                                    innerHeight: window.innerHeight,
                                    outerWidth: window.outerWidth,
                                    outerHeight: window.outerHeight,
                                    screenWidth: screen.width,
                                    screenHeight: screen.height,
                                    availWidth: screen.availWidth,
                                    availHeight: screen.availHeight,
                                    visualViewportWidth: window.visualViewport?.width,
                                    visualViewportHeight: window.visualViewport?.height,
                                    clientWidth: document.documentElement.clientWidth,
                                    clientHeight: document.documentElement.clientHeight,
                                    bodyWidth: document.body.offsetWidth,
                                    bodyHeight: document.body.offsetHeight,
                                    devicePixelRatio: window.devicePixelRatio,
                                    zoom: document.body.style.zoom,
                                    transform: getComputedStyle(document.body).transform,
                                    pageScale: window.visualViewport ? window.visualViewport.scale : null
                                };
                            }
                        """)
                        
                        logger.info(f"N11 diagnostics after goto(): {diagnostics}")
                        
                        # Additional diagnostic information
                        additional_diagnostics = await page.evaluate("""
                            () => {
                                return {
                                    bodyZoom: getComputedStyle(document.body).zoom,
                                    documentElementZoom: getComputedStyle(document.documentElement).zoom,
                                    isMobileMedia: window.matchMedia("(max-width: 768px)").matches,
                                    isTabletMedia: window.matchMedia("(max-width: 992px)").matches,
                                    isDesktopMedia: window.matchMedia("(max-width: 1200px)").matches
                                };
                            }
                        """)
                        
                        logger.info(f"N11 additional diagnostics after goto(): {additional_diagnostics}")
                    except Exception as e:
                        logger.error(f"Failed to collect diagnostics: {e}")
                    
                    # Wait for document to finish loading and network to be idle
                    await page.wait_for_function('document.readyState === "complete"', timeout=10000)
                    await page.wait_for_load_state("domcontentloaded")
                    
                    # Poll for cart elements for up to 5 seconds (250ms intervals)
                    logger.info("Polling for cart elements...")
                    start_time = await page.evaluate('Date.now()')
                    elements_found = False
                    
                    while not elements_found and (await page.evaluate('Date.now()') - start_time) < 1500:
                        # Check if any of the expected cart elements exist
                        expected_elements = [
                            ".cartCouponWrapper",  # Main cart wrapper
                            "button:has-text('Kuponlarım')",  # Coupon button text
                            "input.coupons-main-input"  # Coupon input field
                        ]
                        
                        for element_selector in expected_elements:
                            try:
                                element = await page.query_selector(element_selector)
                                if element and await element.is_visible():
                                    elements_found = True
                                    logger.info(f"[N11] Cart page validated successfully.")
                                    break
                            except Exception:
                                continue
                        
                        if not elements_found:
                            await page.wait_for_timeout(250)  # Poll every 250ms
                    
                    # If we found elements, consider the page valid and proceed with validation
                    if elements_found:
                        # Validate that this is actually the real cart page and not a Cloudflare error
                        is_valid_page = await self._validate_n11_cart_page(page)
                        if is_valid_page:
                            page_loaded = True
                            logger.info("Valid N11 cart page confirmed")
                        else:
                            retry_count += 1
                            if retry_count < max_retries:
                                logger.warning(f"Invalid page detected, retrying ({retry_count}/{max_retries})...")
                                await page.wait_for_timeout(10000)  # Wait 10 seconds before retry
                            else:
                                logger.error("Failed to load cart after 3 attempts")
                                return {
                                    "success": False,
                                    "message": "Failed to load cart after 3 attempts",
                                    "coupon": coupon,
                                    "status": "unknown"
                                }
                    else:
                        # If we didn't find elements, run the existing validation logic
                        logger.warning("Cart elements not found within 5 seconds, running validation...")
                        is_valid_page = await self._validate_n11_cart_page(page)
                        if is_valid_page:
                            page_loaded = True
                            logger.info("Valid N11 cart page confirmed")
                        else:
                            retry_count += 1
                            if retry_count < max_retries:
                                logger.warning(f"Invalid page detected, retrying ({retry_count}/{max_retries})...")
                                await page.wait_for_timeout(10000)  # Wait 10 seconds before retry
                            else:
                                logger.error("Failed to load cart after 3 attempts")
                                return {
                                    "success": False,
                                    "message": "Failed to load cart after 3 attempts",
                                    "coupon": coupon,
                                    "status": "unknown"
                                }
                            
                except Exception as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.warning(f"Navigation error, retrying ({retry_count}/{max_retries}): {e}")
                        await page.wait_for_timeout(10000)  # Wait 10 seconds before retry
                    else:
                        logger.error("Failed to load cart after 3 attempts")
                        return {
                            "success": False,
                            "message": f"Failed to load cart after 3 attempts: {str(e)}",
                            "coupon": coupon,
                            "status": "unknown"
                        }
            
            # Wait for cart to be fully loaded (only if page was successfully loaded)
            if page_loaded:
                await page.wait_for_load_state("domcontentloaded")
            
            # DEBUG: Dump the DOM for inspection before proceeding with selectors
            logger.info("Dumping DOM for debugging...")
            try:
                # Get and log the first 10000 characters of the HTML
                html_content = await page.content()
                logger.info(f"Page HTML (first 10000 chars): {html_content[:10000]}")
                
                # Save full HTML to file for inspection
                import os
                os.makedirs("artifacts", exist_ok=True)
                with open("artifacts/n11_page.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                logger.info("Full page content saved to artifacts/n11_page.html")
                
                # Take screenshot for visual inspection
                await page.screenshot(path="artifacts/n11_page.png", full_page=True)
                logger.info("Page screenshot saved to artifacts/n11_page.png")
                
            except Exception as e:
                logger.error(f"Error during DOM dump: {e}")
            
             # Open the coupon panel before attempting to find input
            logger.info("Opening coupon panel")
            try:
                # Wait for and click the coupon panel (identified by visible text or wrapper)
                coupon_panel_selectors = [
                    ".cartCouponWrapper",
                    "button:has-text('Kuponlarım')",
                    "button:has-text('UçUç Puan')"
                ]
                
                panel_clicked = False
                for i, selector in enumerate(coupon_panel_selectors):
                    try:
                        logger.info(f"Trying selector #{i+1}: {selector}")
                        start_time = await page.evaluate('Date.now()')
                        panel_element = await page.wait_for_selector(selector, timeout=10000)
                        end_time = await page.evaluate('Date.now()')
                        elapsed = end_time - start_time
                        logger.info(f"Selector #{i+1} '{selector}' took {elapsed} ms to find element")
                        if panel_element and await panel_element.is_visible():
                            logger.info(f"Found coupon panel with selector: {selector}")
                            await panel_element.click()
                            panel_clicked = True
                            break
                    except Exception as e:
                        end_time = await page.evaluate('Date.now()')
                        elapsed = end_time - start_time
                        logger.debug(f"Panel check failed for {selector} after {elapsed} ms: {e}")
                        continue
                
                if not panel_clicked:
                    logger.warning("Could not find coupon panel using standard selectors")
                    # Try a more general approach - look for any button that might be a coupon panel opener
                    try:
                        buttons = await page.query_selector_all("button")
                        for btn in buttons:
                            text_content = await btn.inner_text()
                            if "kupon" in text_content.lower() or "coupon" in text_content.lower():
                                logger.info(f"Found potential coupon panel button: {text_content}")
                                await btn.click()
                                panel_clicked = True
                                break
                    except Exception as e:
                        logger.error(f"Error trying to find coupon panel by text: {e}")
                
                if not panel_clicked:
                    logger.warning("Coupon panel not found - proceeding anyway")
                
                # Wait for the coupon input to become visible (the panel should expand)
                logger.info("Waiting for coupon input to become visible")
                await page.wait_for_selector('input.coupons-main-input', state="visible", timeout=15000)
                logger.info("Coupon input is now visible")
                
            except Exception as e:
                logger.error(f"Error opening coupon panel: {e}")
                # If we can't open the panel, proceed anyway but log the error
                logger.warning("Proceeding without successfully opening coupon panel")
            
            # Find and fill the coupon input field
            logger.info("Finding coupon input")
            
            # Handle any intermediate popups (cookie banners, etc.) that might appear
            logger.info("Checking for and dismissing intermediate popups")
            try:
                # Check for common popup dismiss buttons
                popup_dismiss_selectors = [
                    ".popup-close-button",
                    ".cookie-consent .reject", 
                    ".cookie-consent button:has-text('Reddet')",
                    ".cookie-consent button:has-text('Decline')",
                    "[data-testid='close-popup']",
                    ".modal .close",
                    ".consent-banner .btn",
                    "button:has-text('Kabul Et')",  # Accept button
                    "button:has-text('Accept')",   # Accept button
                    ".cookie-banner .accept-btn",
                    ".cookie-consent .accept"
                ]
                
                for selector in popup_dismiss_selectors:
                    try:
                        dismiss_button = await page.query_selector(selector)
                        if dismiss_button and await dismiss_button.is_visible():
                            logger.info(f"Dismissing popup with selector: {selector}")
                            await dismiss_button.click()
                            await page.wait_for_timeout(1000)  # Wait a bit for the popup to close
                            break  # Dismiss only one popup at a time
                    except Exception as e:
                        logger.debug(f"Popup dismiss check failed for {selector}: {e}")
                        continue
            except Exception as e:
                logger.debug(f"Error checking/dismissing popups: {e}")
            
            # Check if we're still on the cart page and retry navigation if needed
            current_url = page.url
            if "sepet" not in current_url:
                logger.info("Navigating back to cart page after popup dismissal")
                await page.goto(CART_URL, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_load_state("domcontentloaded")
            
            # Find and fill the coupon input field
            logger.info("Finding coupon input")
            
            # Find and fill the coupon input field
            logger.info("Finding coupon input")
            try:
                coupon_input = await page.wait_for_selector(
                    'input.coupons-main-input',
                    state="visible",
                    timeout=10000
                )
                logger.info("Coupon input found")
            except TimeoutError:
                logger.error("Coupon input not found")
                return {
                    "success": False,
                    "message": "Coupon input not found",
                    "coupon": coupon,
                    "status": "error"
                }
            
            # Fill the coupon code
            logger.info(f"Entering coupon code: {coupon}")
            await page.fill('input.coupons-main-input', coupon)
            logger.info("Coupon filled")
            
            # Verify the input value matches the coupon (as requested)
            logger.info("Verifying coupon value")
            input_value = await page.input_value('input.coupons-main-input')
            if input_value != coupon:
                logger.warning(f"Coupon value mismatch: expected {coupon}, got {input_value}")
                # This is not necessarily an error, but we log it for debugging
            else:
                logger.info("Coupon value verified")
            
            # Find and click the apply button
            logger.info("Finding apply button")
            try:
                apply_button = await page.wait_for_selector(
                    'button.coupons-main-button-coupon',
                    state="visible",
                    timeout=10000
                )
                logger.info("Apply button found")
            except TimeoutError:
                logger.error("Apply button not found")
                return {
                    "success": False,
                    "message": "Apply button not found",
                    "coupon": coupon,
                    "status": "error"
                }
            
            # Click the apply button
            logger.info("Clicking apply button")
            await apply_button.click()
            logger.info("Apply clicked")
            
            # Wait for result to appear
            logger.info("Waiting for N11 coupon result")
            await page.wait_for_timeout(2000)  # Give time for the result to show
            
            # NEW: Immediate result detection as requested
            # Wait a short time (300-500ms) after clicking apply
            await page.wait_for_timeout(400)
            
            # FIRST: Check for error toasts immediately
            try:
                logger.info("Checking for immediate error toasts")
                
                # Check for both possible toast selectors
                error_toast_selectors = [
                    ".basketPageErrorToast",
                    ".swal2-container.swal2-toast"
                ]
                
                toast_found = False
                error_text = ""
                
                for selector in error_toast_selectors:
                    try:
                        error_toast = page.locator(selector)
                        if await error_toast.is_visible():
                            logger.info(f"Error toast found with selector: {selector}")
                            toast_found = True
                            
                            # Extract the text from the toast
                            try:
                                text_element = error_toast.locator(".text")
                                if await text_element.is_visible():
                                    error_text = await text_element.inner_text()
                                    logger.info(f"Error toast text: {error_text}")
                                else:
                                    # If no .text element, try to get text from the toast itself
                                    error_text = await error_toast.inner_text()
                                    logger.info(f"Error toast text (from toast itself): {error_text}")
                            except Exception as e:
                                logger.warning(f"Could not extract text from toast: {e}")
                                error_text = "Error applying coupon"
                            
                            # Log the raw result
                            logger.info(f"[N11] Raw result: \"{error_text}\"")
                            
                            # Classify and return immediately
                            classified_status = classify_result(error_text, "n11")
                            logger.info(f"[N11] Classification: {classified_status.value}")
                            
                            if classified_status == CouponStatus.SUCCESS:
                                return {
                                    "success": True,
                                    "message": error_text,
                                    "coupon": coupon,
                                    "status": "success"
                                }
                            elif classified_status in [CouponStatus.INVALID, CouponStatus.ALREADY_USED, 
                                                      CouponStatus.EXPIRED, CouponStatus.MIN_CART]:
                                return {
                                    "success": False,
                                    "message": error_text,
                                    "coupon": coupon,
                                    "status": classified_status.value.lower()
                                }
                            else:
                                # For unknown cases, return UNKNOWN status
                                logger.info("Unknown classification result; returning UNKNOWN")
                                return {
                                    "success": False,
                                    "message": error_text,
                                    "coupon": coupon,
                                    "status": "unknown"
                                }
                    except Exception as e:
                        logger.debug(f"Error checking for toast with selector {selector}: {e}")
                        continue
                
                if not toast_found:
                    logger.info("No immediate error toast found")
                    
            except Exception as e:
                logger.error(f"Error during immediate toast check: {e}")
            
            # ONLY IF NO TOAST FOUND, then check for success state
            try:
                logger.info("Checking for success state")
                applied_wrapper = page.locator(".cartCouponWrapper.applied")
                await applied_wrapper.wait_for(timeout=5000)  # Wait up to 5 seconds for wrapper
                
                if await applied_wrapper.is_visible():
                    logger.info("Success detected in cartCouponWrapper.applied")
                    
                    # Extract title and description from the success element
                    try:
                        title_element = page.locator(".cartCouponWrapper.applied .title")
                        description_element = page.locator(".cartCouponWrapper.applied .description")
                        
                        title = ""
                        description = ""
                        
                        if await title_element.is_visible():
                            title = await title_element.inner_text()
                            logger.info(f"Success title: {title}")
                        
                        if await description_element.is_visible():
                            description = await description_element.inner_text()
                            logger.info(f"Success description: {description}")
                        
                        # Combine both texts for logging
                        raw_result = (title + " " + description).strip()
                        if not raw_result:
                            raw_result = "Coupon applied successfully"
                            
                        logger.info(f"[N11] Raw result: \"{raw_result}\"")
                        
                        # Classify the result using shared classifier
                        classified_status = classify_result(raw_result, "n11")
                        logger.info(f"[N11] Classification: {classified_status.value}")
                        
                        if classified_status == CouponStatus.SUCCESS:
                            return {
                                "success": True,
                                "message": raw_result,
                                "coupon": coupon,
                                "status": "success"
                            }
                        else:
                            # For cases where success is detected but classification is not SUCCESS
                            # we still treat it as a successful redemption (the coupon was applied)
                            logger.info("Coupon applied successfully, but classification differs")
                            return {
                                "success": True,
                                "message": raw_result,
                                "coupon": coupon,
                                "status": "success"
                            }
                    except Exception as e:
                        logger.error(f"Error extracting success message: {e}")
                        # If we can't extract details, still return success
                        return {
                            "success": True,
                            "message": "Coupon applied successfully",
                            "coupon": coupon,
                            "status": "success"
                        }
                else:
                    logger.info("Success wrapper not visible")
            except Exception:
                logger.info("No success wrapper found within 5 seconds")
            
            # PRIORITY 2: Check for error toast (SweetAlert2 container)
            try:
                logger.info("Checking for error toast")
                error_toast = page.locator(".basketPageErrorToast")
                await error_toast.wait_for(timeout=3000)  # Wait up to 3 seconds for toast
                
                if await error_toast.is_visible():
                    logger.info("Error toast found")
                    
                    # Extract text content from the error toast
                    try:
                        error_text = await error_toast.locator(".text").inner_text()
                        logger.info(f"Error toast text: {error_text}")
                        
                        logger.info(f"[N11] Raw result: \"{error_text}\"")
                        
                        # Classify the result using shared classifier
                        classified_status = classify_result(error_text, "n11")
                        logger.info(f"[N11] Classification: {classified_status.value}")
                        
                        # Return properly classified error result
                        if classified_status == CouponStatus.SUCCESS:
                            return {
                                "success": True,
                                "message": error_text,
                                "coupon": coupon,
                                "status": "success"
                            }
                        elif classified_status in [CouponStatus.INVALID, CouponStatus.ALREADY_USED, 
                                                  CouponStatus.EXPIRED, CouponStatus.MIN_CART]:
                            return {
                                "success": False,
                                "message": error_text,
                                "coupon": coupon,
                                "status": classified_status.value.lower()
                            }
                        else:
                            # For unknown cases, return UNKNOWN status
                            logger.info("Unknown classification result; returning UNKNOWN")
                            return {
                                "success": False,
                                "message": error_text,
                                "coupon": coupon,
                                "status": "unknown"
                            }
                    except Exception as e:
                        logger.error(f"Error extracting error toast text: {e}")
                        # If we can't extract the text, fall back to general error handling
                        return {
                            "success": False,
                            "message": "Error applying coupon (unable to extract error details)",
                            "coupon": coupon,
                            "status": "error"
                        }
                else:
                    logger.info("Error toast not visible")
            except Exception:
                logger.info("No error toast found within 3 seconds")
            
            # PRIORITY 3: If neither success nor toast appears, return UNKNOWN
            logger.info("No success or error detected - returning UNKNOWN")
            logger.info("[N11] Raw result: \"No visible message after submission\"")
            logger.info("[N11] Classification: UNKNOWN")
            return {
                "success": False,
                "message": "No visible message after submission",
                "coupon": coupon,
                "status": "unknown"
            }
            
        except Exception as e:
            logger.error(f"Error in N11 automation: {e}")
            return {
                "success": False,
                "message": f"Error during automation: {str(e)}",
                "coupon": coupon,
                "status": "error"
            }


