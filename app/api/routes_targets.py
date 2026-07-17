from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import TargetChannel
from app.schemas import TargetChannelCreate

router = APIRouter(prefix="/targets", tags=["targets"])


@router.get("/")
async def list_targets(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(TargetChannel))
    return result.scalars().all()


@router.post("/")
async def create_target(payload: TargetChannelCreate, session: AsyncSession = Depends(get_session)):
    target = TargetChannel(telegram_id=payload.telegram_id, title=payload.title, kind=payload.kind)
    session.add(target)
    await session.commit()
    await session.refresh(target)
    return target
