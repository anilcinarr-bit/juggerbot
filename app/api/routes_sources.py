from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import SourceChannel
from app.schemas import SourceChannelCreate

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("/")
async def list_sources(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(SourceChannel))
    return result.scalars().all()


@router.post("/")
async def create_source(payload: SourceChannelCreate, session: AsyncSession = Depends(get_session)):
    source = SourceChannel(telegram_id=payload.telegram_id, title=payload.title)
    session.add(source)
    await session.commit()
    await session.refresh(source)
    return source
