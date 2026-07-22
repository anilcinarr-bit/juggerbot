import sys
import asyncio
import logging
from typing import Dict

from fastapi import FastAPI

from app.database import init_db
from app.browser.browser_manager import BrowserManager
from app.browser.exceptions import BrowserUnavailable
from app.telegram.client import connect_client, disconnect_client
from app.telegram.listener import start_listeners, stop_listeners
from app.config import settings
from app.core.logging import logger
from app.api import routes_moderation, routes_rules, routes_sources, routes_targets
from app.models import models
from app.pipeline import pipeline_manager
from app.automation import engine
from app.automation.adapter_router import adapter_router
from app.automation.message_normalizer import MessageNormalizer
from app.automation.coupon_extractor import CouponExtractor
from app.automation.platform_detector import PlatformDetector
from app.pipeline.steps import StepFactory
from app.pipeline.forward_engine import ForwardEngine
from app.models.incoming_message import IncomingMessage
from app.browser.exceptions import BrowserUnavailable

# Create singleton instance of BrowserManager
browser_manager = None

app = FastAPI(
    title="Test App",
    version="0.1.0",
    description="Minimal test"
)


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()
    # Start the browser manager (with graceful error handling)
    try:
        browser_manager = BrowserManager()
        await browser_manager.start()
        print("Browser manager started successfully")
    except Exception as e:
        print(f"Browser manager failed to start: {e}")
        # Don't let browser issues prevent the application from starting
        pass  # Continue with startup even if browser fails


@app.on_event("shutdown")
async def on_shutdown() -> None:
    pass


@app.get("/")
async def root() -> Dict[str, str]:
    return {
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8003)