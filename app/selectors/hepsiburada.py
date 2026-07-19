"""
Hepsiburada specific selectors for browser automation.
All Playwright locators are centralized here to avoid hardcoding in business logic.
"""

# Coupon page selectors
COUPON_PAGE_SELECTORS = {
    "coupon_input_field": "[data-testid='coupon-input']",
    "apply_button": "[data-testid='apply-coupon-button']",
    "coupon_status_message": "[data-testid='coupon-status-message']",
    "coupon_success_message": "[data-testid='coupon-success-message']",
    "coupon_error_message": "[data-testid='coupon-error-message']",
    "login_required_message": "[data-testid='login-required-message']"
}

# General page selectors
GENERAL_SELECTORS = {
    "page_loaded_indicator": "body",
    "navigation_bar": "[data-testid='navigation-bar']",
    "header_logo": "[data-testid='header-logo']"
}

# Coupon redemption page specific selectors
COUPON_REDEMPTION_SELECTORS = {
    "coupon_field": "#couponCode",
    "apply_coupon_button": "button[type='submit'][data-action='apply-coupon']",
    "coupon_code_input": "[name='couponCode']",
    "coupon_result_container": "[data-testid='coupon-result-container']"
}