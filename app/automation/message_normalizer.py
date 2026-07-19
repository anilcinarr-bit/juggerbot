import unicodedata
import re
import logging
from typing import Optional

logger = logging.getLogger("automation.message_normalizer")


class MessageNormalizer:
    """Normalizes Telegram messages into a predictable format before coupon extraction."""

    @staticmethod
    def normalize(text: str) -> str:
        """
        Normalize the input text according to specified rules.
        
        Args:
            text (str): The raw input text to normalize
            
        Returns:
            str: The normalized text
        """
        if not text:
            return ""
            
        # 1. Unicode normalize (NFKC)
        normalized = unicodedata.normalize('NFKC', text)
        
        # 2. Replace Turkish characters
        turkish_chars = {
            'İ': 'I', 'İ': 'I', 'Ş': 'S', 'Ğ': 'G', 'Ü': 'U', 'Ö': 'O', 'Ç': 'C',
            'ı': 'i', 'ş': 's', 'ğ': 'g', 'ü': 'u', 'ö': 'o', 'ç': 'c'
        }
        
        for turkish_char, latin_char in turkish_chars.items():
            normalized = normalized.replace(turkish_char, latin_char)
        
        # 3. Convert CRLF to LF
        normalized = normalized.replace('\r\n', '\n')
        
        # 4. Collapse duplicated spaces
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # 5. Trim beginning/end whitespace
        normalized = normalized.strip()
        
        # 6. Remove duplicated blank lines
        # First, split into lines and filter out empty lines
        lines = normalized.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Join with single newlines
        normalized = '\n'.join(non_empty_lines)
        
        return normalized


# Create a global instance for convenience
normalizer = MessageNormalizer()