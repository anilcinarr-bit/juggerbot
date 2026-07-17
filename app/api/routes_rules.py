from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models import FilterRule, ForwardRule
from app.schemas import ForwardRuleCreate, ForwardRuleOut

router = APIRouter(prefix="/rules", tags=["rules"])


@router.get("/", response_model=list[ForwardRuleOut])
async def list_rules(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(ForwardRule).options(selectinload(ForwardRule.filters)))
    return result.scalars().all()


@router.post("/", response_model=ForwardRuleOut)
async def create_rule(payload: ForwardRuleCreate, session: AsyncSession = Depends(get_session)):
    rule = ForwardRule(
        source_id=payload.source_id,
        target_id=payload.target_id,
        active=payload.active,
        use_llm=payload.use_llm,
        llm_prompt=payload.llm_prompt,
        require_moderation=payload.require_moderation,
    )
    session.add(rule)
    await session.flush()

    for f in payload.filters:
        session.add(FilterRule(rule_id=rule.id, filter_type=f.filter_type, value=f.value))

    await session.commit()
    await session.refresh(rule)
    return rule


@router.patch("/{rule_id}/toggle")
async def toggle_rule(rule_id: int, session: AsyncSession = Depends(get_session)):
    rule = await session.get(ForwardRule, rule_id)
    rule.active = not rule.active
    await session.commit()
    return {"id": rule.id, "active": rule.active}
