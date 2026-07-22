"""
Trendyol platform configuration
"""

# Platform name
PLATFORM_NAME = "trendyol"

# URLs
HOME_URL = "https://www.trendyol.com"
LOGIN_URL = "https://www.trendyol.com/login"
CART_URL = "https://www.trendyol.com/sepet"
COUPON_PAGE_URL = "https://www.trendyol.com/kuponlar"
CHECKOUT_URL = None

# Selectors
COUPON_PANEL_SELECTOR = "#coupon-panel"
COUPON_INPUT_SELECTOR = "input[placeholder='İndirim kodu girin']"  # Based on inspection results
APPLY_BUTTON_SELECTOR = ".basket-top-coupon-action-button"  # From the inspection results
RESULT_SELECTOR = ".coupon-result-message"
LOGIN_INDICATOR_SELECTOR = ".user-menu"
USER_MENU_SELECTOR = ".user-menu"
