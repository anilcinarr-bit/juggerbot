import logging
from typing import Any, Dict
from app.models.incoming_message import IncomingMessage
from app.adapters.base import BaseAdapter

logger = logging.getLogger("adapters.hepsiburada")


class HepsiburadaAdapter(BaseAdapter):
    """Hepsiburada adapter for processing Telegram messages"""
    
    async def execute(self, message: IncomingMessage) -> Dict[str, Any]:
        """
        Execute Hepsiburada-specific logic
        
        Args:
            message: The IncomingMessage to process
            
        Returns:
            Dict containing execution results and metadata
        """
        try:
            # Log that the Hepsiburada adapter is processing the message
            logger.info("HepsiburadaAdapter executing for message")
            logger.info(f"Processing message from {message.chat_title} ({message.chat_id})")
            logger.info(f"Message content: {message.text}")
            
            # Extract coupon from the message
            # This would be handled by the coupon extractor in a real implementation
            # For now, we'll return success for demonstration purposes
            return {
                "status": "success",
                "adapter": "hepsiburada",
                "triggered_by": {
                    "chat_title": message.chat_title,
                    "chat_id": message.chat_id,
                    "sender_name": message.sender_name,
                    "message_text": message.text
                },
                "processed_at": "2026-07-18T00:40:22Z",  # This would be replaced with actual timestamp in real implementation
                "coupon_data": {
                    "coupon_code": message.text.split()[-1] if message.text else None,
                    "extracted": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in HepsiburadaAdapter execution: {e}")
            return {
                "status": "error",
                "adapter": "hepsiburada",
                "error": str(e),
                "triggered_by": {
                    "chat_title": message.chat_title,
                    "chat_id": message.chat_id,
                    "sender_name": message.sender_name
                }
            }
