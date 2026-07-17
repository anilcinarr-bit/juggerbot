import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from telethon import TelegramClient
from telethon.tl.custom.message import Message

from app.filters.engine import message_passes_filters
from app.llm.processor import process_text
from app.models import ForwardRule, MessageLog, MessageStatus, TargetChannel
from app.moderation.queue import add_to_queue

logger = logging.getLogger("forwarder")


async def handle_incoming_message(
    client: TelegramClient,
    session: AsyncSession,
    rule: ForwardRule,
    message: Message,
) -> None:
    """Tek bir kural için gelen mesajı işler: filtrele -> LLM -> moderasyon -> gönder."""

    if rule.filters and not message_passes_filters(message, rule.filters):
        await _log(session, rule.id, message.id, None, MessageStatus.FILTERED_OUT)
        return

    text = message.raw_text
    if rule.use_llm and text:
        try:
            text = await process_text(text, rule.llm_prompt)
        except Exception:
            logger.exception("LLM işleme başarısız oldu, orijinal metin kullanılacak")

    if rule.require_moderation:
        await add_to_queue(session, rule.id, message.id, text, media_path=None)
        await _log(session, rule.id, message.id, None, MessageStatus.PENDING_MODERATION)
        return

    await _send(client, session, rule, message, text)


async def _send(
    client: TelegramClient,
    session: AsyncSession,
    rule: ForwardRule,
    message: Message,
    text: str | None,
) -> None:
    target_result = await session.execute(select(TargetChannel).where(TargetChannel.id == rule.target_id))
    target = target_result.scalar_one()

    try:
        if message.media and text != message.raw_text:
            # LLM metni değiştirdiyse, medyayı yeni caption ile tekrar gönder
            sent = await client.send_file(target.telegram_id, file=message.media, caption=text)
        elif message.media:
            sent = await client.forward_messages(target.telegram_id, message)
        else:
            sent = await client.send_message(target.telegram_id, text or message.raw_text)

        target_msg_id = sent.id if not isinstance(sent, list) else sent[0].id
        await _log(session, rule.id, message.id, target_msg_id, MessageStatus.FORWARDED)
    except Exception:
        logger.exception("Mesaj gönderilemedi, rule_id=%s", rule.id)
        await _log(session, rule.id, message.id, None, MessageStatus.FAILED)


async def _log(
    session: AsyncSession,
    rule_id: int,
    source_msg_id: int,
    target_msg_id: int | None,
    status: MessageStatus,
) -> None:
    session.add(
        MessageLog(
            rule_id=rule_id,
            source_msg_id=source_msg_id,
            target_msg_id=target_msg_id,
            status=status,
        )
    )
    await session.commit()
