"""
Browser-related exceptions
"""

from typing import Optional


class BrowserUnavailable(Exception):
    """Exception raised when browser functionality is not available."""
    
    def __init__(self, message: str = "Browser functionality is currently unavailable"):
        self.message = message
        super().__init__(self.message)