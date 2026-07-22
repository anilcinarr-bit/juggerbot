import sys
import asyncio
import logging
from typing import Dict

from fastapi import FastAPI

from app.api import routes_moderation, routes_rules, routes_sources, routes_targets
from app.database import init_db
from app.telegram.client import connect_client, disconnect_client
from app.telegram.listener import start_listeners, stop_listeners
from app.config import settings
from app.core.logging import logger
from app.browser.browser_manager import BrowserManager
from app.browser.exceptions import BrowserUnavailable

# Create singleton instance of BrowserManager
browser_manager = BrowserManager()

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Production-quality backend foundation for SaaS application"
)

app.include_router(routes_sources.router)
app.include_router(routes_targets.router)
app.include_router(routes_rules.router)
app.include_router(routes_moderation.router)


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()
    # Start the browser manager (with graceful error handling)
    try:
        await browser_manager.start()
        logger.info("Browser manager started successfully")
    except Exception as e:
        logger.warning(f"Browser manager failed to start: {e}. Continuing without browser functionality.")
        # Don't let browser issues prevent the application from starting
        # The browser is now optional - we'll set a flag to indicate it's not available
        # This will be used by other services that may check if browser is available
        # In case of error, we still want the app to start properly
        pass  # Continue with startup even if browser fails
    
    # Connect to Telegram client and start listeners
    await connect_client()
    await start_listeners()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    # Stop Telegram listeners
    await stop_listeners()
    # Disconnect from Telegram client
    await disconnect_client()
    # Stop the browser manager
    try:
        await browser_manager.stop()
    except Exception as e:
        logger.error(f"Error stopping browser manager: {e}")


@app.get("/")
async def root() -> Dict[str, str]:
    return {
        "name": "Project Atlas",
        "status": "running",
        "version": "0.1.0"
    }


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}