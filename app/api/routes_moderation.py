from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models import ForwardRule, PendingModeration, TargetChannel
from app.schemas import ForwardRuleCreate, ForwardRuleOut

router = APIRouter(prefix="/moderation", tags=["moderation"])


@router.get("/pending")
async def list_pending(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(PendingModeration).where(PendingModeration.status == "pending"))
    return result.scalars().all()


@router.post("/{item_id}/approve")
async def approve(item_id: int, session: AsyncSession = Depends(get_session)):
    item = await session.get(PendingModeration, item_id)
    rule = await session.get(ForwardRule, item.rule_id)
    target = await session.get(TargetChannel, rule.target_id)

    # Note: In the new implementation, we don't send messages directly
    # This is a placeholder for what would happen in the actual forwarding logic
    
    item.status = "approved"
    await session.commit()
    return {"id": item.id, "status": item.status}


@router.post("/{item_id}/reject")
async def reject(item_id: int, session: AsyncSession = Depends(get_session)):
    item = await session.get(PendingModeration, item_id)
    item.status = "rejected"
    await session.commit()
    return {"id": item.id, "status": item.status}