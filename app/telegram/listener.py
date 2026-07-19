import logging
from telethon import events

from app.telegram.client import get_telegram_client
from app.telegram.handlers import handle_new_message

logger = logging.getLogger("telegram.listener")


def register_listeners() -> None:
    """Register Telegram event listeners"""
    logger.info("Registering Telegram event listeners...")
    
    # Get the client instance
    client = get_telegram_client()
    
    # Register handler for new messages
    @client.on(events.NewMessage())
    async def message_handler(event):
        await handle_new_message(event)
    
    logger.info("Telegram event listeners registered successfully")


async def start_listeners() -> None:
    """Start the Telegram listeners"""
    try:
        register_listeners()
        logger.info("Telegram listeners started successfully")
    except Exception as e:
        logger.error(f"Failed to start Telegram listeners: {e}")
        raise


async def stop_listeners() -> None:
    """Stop the Telegram listeners"""
    try:
        # The client will be disconnected in the shutdown event
        logger.info("Telegram listeners stopped successfully")
    except Exception as e:
        logger.error(f"Failed to stop Telegram listeners: {e}")
