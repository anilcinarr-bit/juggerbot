"""
Logging configuration for the application.
"""
import logging
from logging.config import dictConfig
from typing import Dict, Any

from app.config import settings

# Define logging configuration
LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "json": {
            "format": "{\"timestamp\": \"%(asctime)s\", \"name\": \"%(name)s\", \"level\": \"%(levelname)s\", \"message\": \"%(message)s\"}",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": settings.log_level,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": settings.log_level,
    },
    "loggers": {
        "app": {
            "handlers": ["console"],
            "level": settings.log_level,
            "propagate": False,
        }
    },
}

# Apply the logging configuration
dictConfig(LOGGING_CONFIG)

# Get a logger instance
logger = logging.getLogger("app")