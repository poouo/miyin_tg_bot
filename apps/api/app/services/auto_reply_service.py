from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.models.entities import AutoReplyRule
from apps.api.app.schemas.auto_reply import AutoReplyRuleCreate, AutoReplyRuleUpdate

ALLOWED_PARSE_MODES = {"plain", "markdownv2", "html"}


def _split_keywords(raw: str) -> list[str]:
    parts = raw.replace("，", ",").split(",")
    values: list[str] = []
    for part in parts:
        item = part.strip().lower()
        if not item:
            continue
        if item in values:
            continue
        values.append(item)
    return values


def _normalize_keyword_field(raw: str) -> str:
    return ",".join(_split_keywords(raw))


def _normalize_parse_mode(raw: str | None) -> str:
    mode = (raw or "plain").strip().lower()
    if mode not in ALLOWED_PARSE_MODES:
        return "plain"
    return mode


async def list_auto_replies(db: AsyncSession, chat_id: int) -> list[AutoReplyRule]:
    result = await db.execute(
        select(AutoReplyRule).where(AutoReplyRule.chat_id == chat_id).order_by(AutoReplyRule.created_at.desc())
    )
    return list(result.scalars().all())


async def create_auto_reply(db: AsyncSession, payload: AutoReplyRuleCreate) -> AutoReplyRule:
    data = payload.model_dump()
    data["keyword"] = _normalize_keyword_field(data.get("keyword", ""))
    data["parse_mode"] = _normalize_parse_mode(data.get("parse_mode"))
    entity = AutoReplyRule(**data)
    db.add(entity)
    await db.commit()
    await db.refresh(entity)
    return entity


async def update_auto_reply(
    db: AsyncSession, chat_id: int, rule_id: int, payload: AutoReplyRuleUpdate
) -> AutoReplyRule | None:
    result = await db.execute(
        select(AutoReplyRule).where(and_(AutoReplyRule.id == rule_id, AutoReplyRule.chat_id == chat_id))
    )
    entity = result.scalar_one_or_none()
    if entity is None:
        return None

    for key, value in payload.model_dump(exclude_unset=True).items():
        if key == "keyword" and isinstance(value, str):
            value = _normalize_keyword_field(value)
        if key == "parse_mode":
            value = _normalize_parse_mode(value)
        setattr(entity, key, value)

    await db.commit()
    await db.refresh(entity)
    return entity


async def delete_auto_reply(db: AsyncSession, chat_id: int, rule_id: int) -> bool:
    result = await db.execute(
        select(AutoReplyRule).where(and_(AutoReplyRule.id == rule_id, AutoReplyRule.chat_id == chat_id))
    )
    entity = result.scalar_one_or_none()
    if entity is None:
        return False

    await db.delete(entity)
    await db.commit()
    return True


async def match_auto_reply(db: AsyncSession, chat_id: int, text: str) -> AutoReplyRule | None:
    content = (text or "").strip().lower()
    if not content:
        return None

    rules = await list_auto_replies(db, chat_id)
    for rule in rules:
        if not rule.enabled:
            continue
        for keyword in _split_keywords(rule.keyword):
            if keyword and keyword in content:
                return rule
    return None
