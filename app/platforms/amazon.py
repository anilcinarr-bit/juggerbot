"""
Amazon platform configuration
"""

# Platform name
PLATFORM_NAME = "amazon"

# URLs
HOME_URL = "https://www.amazon.com"
LOGIN_URL = "https://www.amazon.com/ap/signin"
CART_URL = "https://www.amazon.com/cart"
COUPON_PAGE_URL = None
CHECKOUT_URL = "https://www.amazon.com/checkout"

# Selectors
COUPON_PANEL_SELECTOR = "#coupon-panel"
COUPON_INPUT_SELECTOR = "#coupon-input"
APPLY_BUTTON_SELECTOR = "#apply-coupon-button"
RESULT_SELECTOR = ".coupon-result-message"
LOGIN_INDICATOR_SELECTOR = ".nav-line-1"
USER_MENU_SELECTOR = ".nav-line-1"