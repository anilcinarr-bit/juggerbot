from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PendingModeration


async def add_to_queue(
    session: AsyncSession,
    rule_id: int,
    source_msg_id: int,
    content: str | None,
    media_path: str | None = None,
) -> PendingModeration:
    item = PendingModeration(
        rule_id=rule_id,
        source_msg_id=source_msg_id,
        content=content,
        media_path=media_path,
        status="pending",
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item
