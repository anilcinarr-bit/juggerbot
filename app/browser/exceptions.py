"""
Browser-related exceptions
"""

from typing import Optional


class BrowserUnavailable(Exception):
    """Exception raised when browser functionality is not available."""
    
    def __init__(self, message: str = "Browser functionality is currently unavailable"):
        self.message = message
        super().__init__(self.message)


class BrowserNotConfigured(Exception):
    """Exception raised when browser or profile has not been configured yet."""
    
    def __init__(self, message: str = "No browser/profile has been configured yet."):
        self.message = message
        super().__init__(self.message)
