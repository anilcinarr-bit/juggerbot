import logging
from telethon import TelegramClient

from app.config import settings

logger = logging.getLogger("telegram.client")

# Global variable to track if we've already created the client
_client_instance = None


def get_telegram_client() -> TelegramClient:
    """Get or create a singleton Telegram client instance"""
    global _client_instance
    if _client_instance is None:
        _client_instance = TelegramClient(settings.tg_session_name, settings.tg_api_id, settings.tg_api_hash)
    return _client_instance


async def connect_client() -> None:
    """Connect to Telegram client"""
    try:
        client = get_telegram_client()
        await client.start()
        logger.info("Telegram client connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Telegram: {e}")
        raise


async def disconnect_client() -> None:
    """Disconnect from Telegram client"""
    try:
        client = get_telegram_client()
        await client.disconnect()
        logger.info("Telegram client disconnected successfully")
    except Exception as e:
        logger.error(f"Failed to disconnect from Telegram: {e}")
