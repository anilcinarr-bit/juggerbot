from pydantic import BaseModel

from app.models import FilterType, TargetKind


class SourceChannelCreate(BaseModel):
    telegram_id: int
    title: str = ""


class TargetChannelCreate(BaseModel):
    telegram_id: int
    title: str = ""
    kind: TargetKind = TargetKind.USER


class FilterRuleCreate(BaseModel):
    filter_type: FilterType
    value: str | None = None


class ForwardRuleCreate(BaseModel):
    source_id: int
    target_id: int
    active: bool = True
    use_llm: bool = False
    llm_prompt: str | None = None
    require_moderation: bool = False
    filters: list[FilterRuleCreate] = []


class ForwardRuleOut(BaseModel):
    id: int
    source_id: int
    target_id: int
    active: bool
    use_llm: bool
    require_moderation: bool

    class Config:
        from_attributes = True
