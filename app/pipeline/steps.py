import logging
from app.models.incoming_message import IncomingMessage
from app.pipeline.forward_engine import ForwardEngine

logger = logging.getLogger("pipeline.steps")


async def logger_step(message: IncomingMessage) -> None:
    """Logger step that produces exactly the same output as the original implementation"""
    # Log the message in the required format (exactly as before)
    logger.info("=" * 50)
    logger.info("NEW MESSAGE")
    logger.info("")
    logger.info("Source : " + message.chat_title)
    logger.info("Chat ID : " + str(message.chat_id))
    logger.info("Sender : " + message.sender_name)
    logger.info("")
    logger.info("Message :")
    logger.info("")
    logger.info(message.text)
    logger.info("=" * 50)


async def forward_engine_step(message: IncomingMessage) -> None:
    """Forward Engine step that processes the message through ForwardEngine"""
    # Create and use ForwardEngine instance
    forward_engine = ForwardEngine()
    await forward_engine.process(message)
