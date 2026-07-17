import logging

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from telethon import TelegramClient, events

from app.config import settings
from app.database import async_session
from app.models import ForwardRule, SourceChannel
from app.telegram.forwarder import handle_incoming_message

logger = logging.getLogger("userbot")

client = TelegramClient(settings.tg_session_name, settings.tg_api_id, settings.tg_api_hash)


async def _active_source_ids() -> list[int]:
    async with async_session() as session:
        result = await session.execute(select(SourceChannel.telegram_id))
        return [row[0] for row in result.all()]


async def _rules_for_source(telegram_id: int) -> list[ForwardRule]:
    async with async_session() as session:
        result = await session.execute(
            select(ForwardRule)
            .join(SourceChannel)
            .where(SourceChannel.telegram_id == telegram_id, ForwardRule.active.is_(True))
            .options(selectinload(ForwardRule.filters))
        )
        return list(result.scalars().all())


def register_handlers() -> None:
    @client.on(events.NewMessage())
    async def _on_new_message(event: events.NewMessage.Event) -> None:
        chat = await event.get_chat()
        chat_id = getattr(chat, "id", None)
        if chat_id is None:
            return

        # Telethon "channel id" formatı ile DB'deki ham id farklı olabilir; -100 prefix normalize ediyoruz.
        normalized_id = event.chat_id

        active_ids = await _active_source_ids()
        if normalized_id not in active_ids:
            return

        rules = await _rules_for_source(normalized_id)
        if not rules:
            return

        async with async_session() as session:
            for rule in rules:
                await handle_incoming_message(client, session, rule, event.message)


async def start_userbot() -> None:
    register_handlers()
    await client.start()
    logger.info("Userbot başlatıldı, dinlemede...")
    # main.py bunu bir background task olarak çalıştıracak; burada bloklamıyoruz.
