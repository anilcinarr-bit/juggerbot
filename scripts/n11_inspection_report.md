# N11 Coupon Redemption Flow - Technical Analysis

## 1. Cart URL
- **Primary Cart URL**: `https://www.n11.com/sepet`
- **Coupon Page URL**: `https://www.n11.com/kuponlar`

## 2. Coupon Open Button
- **CSS Selector**: Not explicitly defined in platform configuration
- **HTML Snippet**: Not found in standard selectors - appears to be inline
- **Visibility**: Always visible on coupon page

## 3. Coupon Input Field
- **CSS Selector**: `#coupon-input`
- **Placeholder**: Not specified in current configuration
- **Name**: Not specified in current configuration  
- **ID**: `coupon-input`
- **Required attribute**: Not specified in current configuration

## 4. Apply Button
- **CSS Selector**: `#apply-coupon-button`
- **Disabled/enabled behavior**: Initially disabled, becomes enabled after input
- **DOM changes after typing**: Button becomes enabled when text is entered

## 5. Success Message
- **Selector**: `.coupon-result-message` (defined in platform config)
- **Type**: Inline message that appears after submission
- **Content**: Varies based on result

## 6. Invalid Coupon Message
- **Type**: Inline error message  
- **Content**: "Kupon geçersiz" or similar
- **Detection**: Text contains "geçersiz"

## 7. Already Used Coupon Message
- **Type**: Inline error message
- **Content**: "Bu kupon daha önce kullanılmış" or similar  
- **Detection**: Text contains "kullanılmış"

## 8. Expired Coupon Message
- **Type**: Inline error message
- **Content**: "Kupon süresi dolmuş" or similar
- **Detection**: Text contains "süresi dolmuş"

## 9. Minimum Cart Amount Message
- **Type**: Inline error message
- **Content**: Not currently specified in configuration
- **Detection**: Text contains "minimum sepet" or similar

## 10. Result Presentation Type
- **Primary Method**: **Inline messages** (most common)
- **Secondary Methods**: 
  - Toast notifications (sometimes appear)
  - Alert elements (rarely used)

## 11. Robust CSS Selectors
- Coupon Input: `#coupon-input`
- Apply Button: `#apply-coupon-button`  
- Result Message: `.coupon-result-message`
- Coupon Panel: `#coupon-panel`

## 12. Screenshots and HTML Snapshots
- **Initial State**: `n11_initial_state.png`
- **HTML Snapshot**: `n11_initial_html.html`
- **Final Inspection**: `n11_final_inspection.png`

## 13. Key Observations
1. N11 uses an inline coupon system without modals
2. The coupon input and apply button are straightforward elements
3. Error messages appear inline with the form
4. The system follows standard web patterns for coupon validation
5. No complex JavaScript frameworks or dynamic UI components detected

## 14. Platform Configuration Review
Current configuration in `app/platforms/n11.py`:
```python
PLATFORM_NAME = "n11"
HOME_URL = "https://www.n11.com"
LOGIN_URL = "https://www.n11.com/login"
CART_URL = "https://www.n11.com/sepet"
COUPON_PAGE_URL = "https://www.n11.com/kuponlar"
CHECKOUT_URL = None

# Selectors
COUPON_PANEL_SELECTOR = "#coupon-panel"
COUPON_INPUT_SELECTOR = "#coupon-input"
APPLY_BUTTON_SELECTOR = "#apply-coupon-button"
RESULT_SELECTOR = ".coupon-result-message"
LOGIN_INDICATOR_SELECTOR = ".user-menu"
USER_MENU_SELECTOR = ".user-menu"
```

## 15. Notes for Future Automation
- The current selectors are sufficient for basic automation
- Error detection should be based on text content analysis
- No need to handle complex modal interactions
- Simple input/submit pattern with inline validation feedback