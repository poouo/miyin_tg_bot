from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.models.entities import KeywordRule
from apps.api.app.services.keyword_service import list_keywords


async def match_keyword_rule(db: AsyncSession, chat_id: int, text: str) -> KeywordRule | None:
    content = (text or "").lower()
    if not content:
        return None

    rules = await list_keywords(db, chat_id)
    for rule in rules:
        if not rule.enabled:
            continue
        if rule.keyword.lower() in content:
            return rule
    return None

