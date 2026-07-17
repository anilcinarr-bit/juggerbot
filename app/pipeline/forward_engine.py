import logging
from app.models.incoming_message import IncomingMessage
from app.pipeline.telegram_sender import TelegramSender
from app.pipeline.pipeline_manager import PipelineManager

logger = logging.getLogger("pipeline.forward_engine")


class ForwardEngine:
    """Forward engine that processes messages and forwards them to target chats"""
    
    def __init__(self):
        self.pipeline_manager = PipelineManager()
        
    async def process(self, message: IncomingMessage) -> bool:
        """
        Process a message and forward it if there's a matching pipeline
        
        Args:
            message: The IncomingMessage to process
            
        Returns:
            bool: True if message was forwarded, False otherwise
        """
        try:
            # Find pipeline by source chat ID
            pipeline = self.pipeline_manager.get_pipeline_by_source(message.chat_id)
            
            if not pipeline:
                logger.info(f"No pipeline found for source chat {message.chat_id}, ignoring message")
                return False
            
            if not pipeline.enabled:
                logger.info(f"Pipeline for source chat {message.chat_id} is disabled, ignoring message")
                return False
                
            # Forward the message to target chat
            telegram_sender = TelegramSender()
            success = await telegram_sender.send(message, pipeline.target_chat_id)
            
            if success:
                logger.info(f"Pipeline: {pipeline.name}\nSource: {message.chat_title} ({message.chat_id})\nTarget: {pipeline.target_chat_id}")
            else:
                logger.error(f"Failed to forward message from {message.chat_title} ({message.chat_id}) to {pipeline.target_chat_id}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return False