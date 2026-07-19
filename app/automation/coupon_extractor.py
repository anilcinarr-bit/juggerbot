import re
import logging
from typing import List

logger = logging.getLogger("automation.coupon_extractor")

class CouponExtractor:
    """Generic coupon extraction engine that detects various coupon code formats."""
    
    def __init__(self):
        # Define specific regex patterns for different coupon formats
        self.patterns = [
            r'\b[A-Z]{4,}-\d{4}-[A-Z]{4,}\b',  # ABCD-1234-EFGH (most specific first)
            r'\b[A-Z]{3,}-\d{1,}\b',           # HEPSI-1234, HEPSI-500 (more flexible number pattern)
            r'\b[A-Z]{3,}\d{2,}\b',           # ABC123, SAVE50
            r'\b[A-Z]{3,}\d{4}\b',           # WELCOME2026
            r'\b[A-Z]{5,}\d{2,}\b',          # INDIRIM25
        ]
        
        # Combine all patterns into one regex for efficiency
        self.combined_pattern = re.compile('|'.join(self.patterns), re.IGNORECASE)
    
    def extract(self, text: str) -> List[str]:
        """
        Extract coupon codes from the given text.
        
        Args:
            text (str): The input text to search for coupon codes
            
        Returns:
            list[str]: List of unique coupon codes found, or empty list if none found
        """
        if not text:
            logger.info("No coupon detected.")
            return []
        
        # Find all matches using the combined pattern
        matches = self.combined_pattern.findall(text)
        
        # Remove duplicates while preserving order
        unique_coupons = list(dict.fromkeys(matches))
        
        # Log results
        if unique_coupons:
            for coupon in unique_coupons:
                logger.info(f"Coupon detected: {coupon}")
        else:
            logger.info("No coupon detected.")
            
        return unique_coupons

# Create a global instance for convenience
extractor = CouponExtractor()
