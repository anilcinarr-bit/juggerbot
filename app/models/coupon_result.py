import enum
from typing import Optional
from pydantic import BaseModel


class CouponStatus(str, enum.Enum):
    """Enumeration of coupon redemption statuses"""
    SUCCESS = "SUCCESS"
    INVALID = "INVALID"
    ALREADY_USED = "ALREADY_USED"
    EXPIRED = "EXPIRED"
    MIN_CART = "MIN_CART"
    UNKNOWN = "UNKNOWN"


class CouponResult(BaseModel):
    """Model representing a coupon redemption result"""
    success: bool
    message: str
    coupon: str
    status: CouponStatus
    
    class Config:
        use_enum_values = True


def classify_hepsiburada_result(raw_message: str) -> CouponStatus:
    """
    Classify Hepsiburada coupon redemption result into common statuses
    
    Args:
        raw_message: Raw message from Hepsiburada platform
        
    Returns:
        CouponStatus: Classified status
    """
    if not raw_message:
        return CouponStatus.UNKNOWN
    
    normalized_text = raw_message.strip().lower()
    
    # Mapping for Hepsiburada specific messages to common statuses
    classifications = {
        "kupon başarıyla uygulandı.": CouponStatus.SUCCESS,
        "bu kupon daha önce kullanıldı.": CouponStatus.ALREADY_USED,
        "kupon geçersiz.": CouponStatus.INVALID,
        "geçersiz bir kod girdin": CouponStatus.INVALID,
    }
    
    # Check for exact matches first
    if normalized_text in classifications:
        return classifications[normalized_text]
    
    # Check for partial matches
    if "kupon başarıyla uygulandı" in normalized_text:
        return CouponStatus.SUCCESS
    elif "daha önce kullanıldı" in normalized_text:
        return CouponStatus.ALREADY_USED
    elif "geçersiz" in normalized_text:
        return CouponStatus.INVALID
    elif "süresi dolmuş" in normalized_text:
        return CouponStatus.EXPIRED
    elif "minimum sepet tutarı" in normalized_text:
        return CouponStatus.MIN_CART
    
    # Default case
    return CouponStatus.UNKNOWN


def classify_trendyol_result(raw_message: str) -> CouponStatus:
    """
    Classify Trendyol coupon redemption result into common statuses
    
    Args:
        raw_message: Raw message from Trendyol platform
        
    Returns:
        CouponStatus: Classified status
    """
    if not raw_message:
        return CouponStatus.UNKNOWN
    
    # Normalize the text for comparison (lowercase, remove extra whitespace)
    normalized = raw_message.strip().lower()
    
    # Check for specific patterns in the normalized text
    if "başarıyla uygulandı" in normalized:
        return CouponStatus.SUCCESS
    elif "daha önce kullan" in normalized:
        return CouponStatus.ALREADY_USED
    elif "geçersiz" in normalized:
        return CouponStatus.INVALID
    elif "süresi dol" in normalized:
        return CouponStatus.EXPIRED
    elif "minimum sepet" in normalized:
        return CouponStatus.MIN_CART
    else:
        # Default to UNKNOWN for unrecognized results
        return CouponStatus.UNKNOWN


def classify_n11_result(raw_message: str) -> CouponStatus:
    """
    Classify N11 coupon redemption result into common statuses
    
    Args:
        raw_message: Raw message from N11 platform
        
    Returns:
        CouponStatus: Classified status
    """
    if not raw_message:
        return CouponStatus.UNKNOWN
    
    # Normalize the text for comparison (lowercase, remove extra whitespace)
    normalized = raw_message.strip().lower()
    
    # Check for specific patterns in the normalized text
    if "kupon başarıyla uygulandı" in normalized or "coupon applied successfully" in normalized:
        return CouponStatus.SUCCESS
    elif "daha önce kullanıldı" in normalized or "already used" in normalized:
        return CouponStatus.ALREADY_USED
    elif "geçersiz" in normalized or "invalid" in normalized:
        return CouponStatus.INVALID
    elif "süresi dolmuş" in normalized or "expired" in normalized:
        return CouponStatus.EXPIRED
    elif "minimum sepet tutarı" in normalized or "minimum cart amount" in normalized:
        return CouponStatus.MIN_CART
    else:
        # Default to UNKNOWN for unrecognized results
        return CouponStatus.UNKNOWN


def classify_result(raw_message: str, platform: str) -> CouponStatus:
    """
    Classify coupon result based on platform
    
    Args:
        raw_message: Raw message from platform
        platform: Platform name (hepsiburada, trendyol or n11)
        
    Returns:
        CouponStatus: Classified status
    """
    if platform.lower() == "hepsiburada":
        return classify_hepsiburada_result(raw_message)
    elif platform.lower() == "trendyol":
        return classify_trendyol_result(raw_message)
    elif platform.lower() == "n11":
        return classify_n11_result(raw_message)
    else:
        return CouponStatus.UNKNOWN
