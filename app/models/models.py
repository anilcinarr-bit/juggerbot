import datetime as dt
import enum

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TargetKind(str, enum.Enum):
    USER = "user"  # bağlı hesap üzerinden gönderim
    BOT = "bot"    # bot token üzerinden gönderim


class FilterType(str, enum.Enum):
    KEYWORD_INCLUDE = "keyword_include"
    KEYWORD_EXCLUDE = "keyword_exclude"
    MEDIA_ONLY = "media_only"
    TEXT_ONLY = "text_only"


class MessageStatus(str, enum.Enum):
    FORWARDED = "forwarded"
    FILTERED_OUT = "filtered_out"
    PENDING_MODERATION = "pending_moderation"
    REJECTED = "rejected"
    FAILED = "failed"


class SourceChannel(Base):
    __tablename__ = "source_channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255), default="")
    added_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)

    rules: Mapped[list["ForwardRule"]] = relationship(back_populates="source")


class TargetChannel(Base):
    __tablename__ = "target_channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255), default="")
    kind: Mapped[TargetKind] = mapped_column(Enum(TargetKind), default=TargetKind.USER)
    added_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)


class ForwardRule(Base):
    __tablename__ = "forward_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("source_channels.id"))
    target_id: Mapped[int] = mapped_column(ForeignKey("target_channels.id"))
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    use_llm: Mapped[bool] = mapped_column(Boolean, default=False)
    llm_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)

    require_moderation: Mapped[bool] = mapped_column(Boolean, default=False)

    source: Mapped["SourceChannel"] = relationship(back_populates="rules")
    target: Mapped["TargetChannel"] = relationship()
    filters: Mapped[list["FilterRule"]] = relationship(back_populates="rule", cascade="all, delete-orphan")


class FilterRule(Base):
    __tablename__ = "filter_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rule_id: Mapped[int] = mapped_column(ForeignKey("forward_rules.id"))
    filter_type: Mapped[FilterType] = mapped_column(Enum(FilterType))
    value: Mapped[str | None] = mapped_column(String(255), nullable=True)

    rule: Mapped["ForwardRule"] = relationship(back_populates="filters")


class MessageLog(Base):
    __tablename__ = "message_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rule_id: Mapped[int] = mapped_column(ForeignKey("forward_rules.id"))
    source_msg_id: Mapped[int] = mapped_column(BigInteger)
    target_msg_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    status: Mapped[MessageStatus] = mapped_column(Enum(MessageStatus))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)


from pydantic import BaseModel
from typing import Optional

class PendingModeration(Base):
    __tablename__ = "pending_moderation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rule_id: Mapped[int] = mapped_column(ForeignKey("forward_rules.id"))
    source_msg_id: Mapped[int] = mapped_column(BigInteger)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)


class PipelineConfig(BaseModel):
    """Configuration for a forwarding pipeline"""
    id: int
    name: str
    enabled: bool
    source_chat_id: int
    target_chat_id: int
    
