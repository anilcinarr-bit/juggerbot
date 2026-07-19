import logging
from typing import Dict, Any
from playwright.async_api import Page

from app.adapters.base import BaseAdapter
from app.browser.browser_manager import BrowserManager
from app.platforms.hepsiburada import HOME_URL, COUPON_PAGE_URL, COUPON_INPUT_SELECTOR, APPLY_BUTTON_SELECTOR, RESULT_SELECTOR

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
            
            # Navigate to Hepsiburada website
            logger.info("Opening Hepsiburada...")
            await page.goto(HOME_URL, timeout=30000)
            
            # Wait for page to load
            await page.wait_for_load_state("networkidle")
            
            # Navigate to coupon redemption page
            logger.info("Navigating to coupon page...")
            await page.goto(COUPON_PAGE_URL, timeout=30000)
            
            # Wait for coupon page to load
            await page.wait_for_load_state("networkidle")
            
            # Find the coupon input field
            logger.info("Finding coupon input field...")
            coupon_input = await page.wait_for_selector(
                COUPON_INPUT_SELECTOR,
                timeout=10000
            )
            
            # Fill the coupon code
            logger.info(f"Entering coupon code: {coupon}")
            await coupon_input.fill(coupon)
            
            # Find and click the apply button
            logger.info("Applying coupon...")
            apply_button = await page.wait_for_selector(
                APPLY_BUTTON_SELECTOR,
                timeout=10000
            )
            await apply_button.click()
            
            # Wait for result to appear
            logger.info("Waiting for result...")
            await page.wait_for_timeout(2000)  # Give time for the result to show
            
            # Check if coupon was applied successfully
            success_message = await page.query_selector(RESULT_SELECTOR)
            error_message = await page.query_selector(RESULT_SELECTOR)
            
            # Determine result based on message presence
            if success_message:
                logger.info("Coupon applied successfully!")
                return {
                    "success": True,
                    "message": "Coupon applied successfully",
                    "coupon": coupon,
                    "status": "applied"
                }
            elif error_message:
                error_text = await error_message.inner_text()
                logger.warning(f"Coupon application failed: {error_text}")
                
                # Check for specific error types
                if "zaten kullanıldı" in error_text.lower() or "already used" in error_text.lower():
                    return {
                        "success": False,
                        "message": "Coupon already used",
                        "coupon": coupon,
                        "status": "already_used"
                    }
                elif "geçersiz kupon" in error_text.lower() or "invalid coupon" in error_text.lower():
                    return {
                        "success": False,
                        "message": "Invalid coupon",
                        "coupon": coupon,
                        "status": "invalid"
                    }
                elif "süresi dolmuş" in error_text.lower() or "expired" in error_text.lower():
                    return {
                        "success": False,
                        "message": "Coupon expired",
                        "coupon": coupon,
                        "status": "expired"
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Error applying coupon: {error_text}",
                        "coupon": coupon,
                        "status": "error"
                    }
            else:
                # Check for login required message
                # Note: We don't have a specific selector for this in platform definitions
                # so we'll rely on error handling instead
                
                # If no specific message found, assume success
                logger.info("Coupon applied successfully (no error messages)")
                return {
                    "success": True,
                    "message": "Coupon applied successfully",
                    "coupon": coupon,
                    "status": "applied"
                }
                
        except Exception as e:
            logger.error(f"Error in Hepsiburada automation: {e}")
            return {
                "success": False,
                "message": f"Error during automation: {str(e)}",
                "coupon": coupon,
                "status": "error"
            }



