import logging
from telethon import TelegramClient

from app.config import settings

logger = logging.getLogger("telegram.client")

# Create the Telegram client instance
client = TelegramClient(settings.tg_session_name, settings.tg_api_id, settings.tg_api_hash)


async def connect_client() -> None:
    """Connect to Telegram client"""
    try:
        await client.start()
        logger.info("Telegram client connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Telegram: {e}")
        raise


async def disconnect_client() -> None:
    """Disconnect from Telegram client"""
    try:
        await client.disconnect()
        logger.info("Telegram client disconnected successfully")
    except Exception as e:
        logger.error(f"Failed to disconnect from Telegram: {e}")