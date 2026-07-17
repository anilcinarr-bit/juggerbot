"""Bir mesajın, bir kurala bağlı filtrelerden geçip geçmediğini belirler."""
from telethon.tl.custom.message import Message

from app.models import FilterRule, FilterType


def message_passes_filters(message: Message, filters: list[FilterRule]) -> bool:
    """Tüm filtreler AND mantığıyla değerlendirilir.
    keyword_include: en az biri metinde geçmeli
    keyword_exclude: hiçbiri metinde geçmemeli
    media_only: mesajda medya olmalı
    text_only: mesajda medya olmamalı
    """
    text = (message.raw_text or "").lower()

    include_terms = [f.value.lower() for f in filters if f.filter_type == FilterType.KEYWORD_INCLUDE and f.value]
    exclude_terms = [f.value.lower() for f in filters if f.filter_type == FilterType.KEYWORD_EXCLUDE and f.value]
    media_only = any(f.filter_type == FilterType.MEDIA_ONLY for f in filters)
    text_only = any(f.filter_type == FilterType.TEXT_ONLY for f in filters)

    if include_terms and not any(term in text for term in include_terms):
        return False

    if exclude_terms and any(term in text for term in exclude_terms):
        return False

    if media_only and not message.media:
        return False

    if text_only and message.media:
        return False

    return True
