import logging
from typing import Optional

from app.models.incoming_message import IncomingMessage
from app.telegram.client import get_telegram_client

logger = logging.getLogger("pipeline.telegram_sender")


class TelegramSender:
    """Telegram sender service for forwarding messages"""
    
    async def send(self, message: IncomingMessage, target_chat_id: int) -> bool:
        """
        Send a message to the specified target chat
        
        Args:
            message: The IncomingMessage to forward
            target_chat_id: The ID of the target chat
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the client instance
            client = get_telegram_client()
            
            # Send the message to the target chat using the shared client
            await client.send_message(
                entity=target_chat_id,
                message=message.text
            )
            
            logger.info(f"Message forwarded successfully to chat {target_chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to forward message to chat {target_chat_id}: {e}")
            return False
