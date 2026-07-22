"""
Hepsiburada platform configuration
"""

# Platform name
PLATFORM_NAME = "hepsiburada"

# URLs
HOME_URL = "https://www.hepsiburada.com"
LOGIN_URL = "https://www.hepsiburada.com/giris"
CART_URL = "https://www.hepsiburada.com/sepetim"  # Updated to cart page for coupon redemption
COUPON_PAGE_URL = "https://www.hepsiburada.com/kuponlar"
CHECKOUT_URL = "https://checkout.hepsiburada.com/sepetim"  # Use the cart page directly

# Selectors - Updated based on verified DOM inspection
COUPON_PANEL_SELECTOR = '[id^="BasketCoupons_"]'  # Dynamic ID pattern from inspection
COUPON_INPUT_SELECTOR = 'input[placeholder="Kupon kodunuzu girin"]'
APPLY_BUTTON_SELECTOR = 'button[type="submit"]'  # This will be scoped to the drawer
RESULT_SELECTOR = ".coupon-result-message"
LOGIN_INDICATOR_SELECTOR = ".user-menu"
USER_MENU_SELECTOR = ".user-menu"