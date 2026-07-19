import logging
from app.models.incoming_message import IncomingMessage
from app.automation.engine import AutomationEngine
from app.adapters.hepsiburada import HepsiburadaAdapter

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
    """Forward Engine step that processes the message through AutomationEngine"""
    # Create and use AutomationEngine instance
    automation_engine = AutomationEngine()
    
    # Execute the automation engine which will create and execute HepsiburadaAdapter
    await automation_engine.execute(message)
