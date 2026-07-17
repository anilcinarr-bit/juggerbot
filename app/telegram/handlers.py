import logging
from telethon import events

from app.models.incoming_message import IncomingMessage
from app.pipeline.pipeline import Pipeline
from app.pipeline.steps import logger_step, forward_engine_step

logger = logging.getLogger("telegram.handlers")


async def handle_new_message(event: events.NewMessage.Event) -> None:
    """Handle new Telegram message events and convert to IncomingMessage then process through pipeline"""
    try:
        # Get chat information
        chat = await event.get_chat()
        chat_title = getattr(chat, "title", "Unknown Chat")
        chat_id = getattr(chat, "id", "Unknown ID")
        
        # Get sender information
        sender = await event.get_sender()
        sender_name = getattr(sender, "first_name", "Unknown Sender")
        if hasattr(sender, "last_name") and sender.last_name:
            sender_name += f" {sender.last_name}"
        
        # Get message content
        message_text = event.message.text or ""
        
        # Create IncomingMessage object
        incoming_message = IncomingMessage(
            message_id=event.message.id,
            chat_id=chat_id,
            chat_title=chat_title,
            sender_id=getattr(sender, "id", None),
            sender_name=sender_name,
            text=message_text,
            date=event.message.date,
            has_media=bool(event.message.media),
            raw_event=event
        )
        
        # Process through pipeline with ForwardEngine first, then LoggerStep
        pipeline = Pipeline([forward_engine_step, logger_step])
        await pipeline.process(incoming_message)
        
    except Exception as e:
        logger.error(f"Error handling new message: {e}")
