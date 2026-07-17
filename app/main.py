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
    # Connect to Telegram client
    await connect_client()
    # Start Telegram listeners
    await start_listeners()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    # Stop Telegram listeners
    await stop_listeners()
    # Disconnect from Telegram client
    await disconnect_client()


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
