from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.models.entities import KeywordRule
from apps.api.app.schemas.keyword import KeywordRuleCreate, KeywordRuleUpdate, validate_keyword_actions


ACTION_FIELDS = {"delete_message", "mute_user", "ban_user"}


def _apply_legacy_action(data: dict, fields_set: set[str]) -> None:
    if "action" not in data or not ACTION_FIELDS.isdisjoint(fields_set):
        return
    action = data["action"]
    data["delete_message"] = True
    data["mute_user"] = action == "mute"
    data["ban_user"] = action == "ban"


def _sync_legacy_action(data: dict) -> None:
    if data.get("ban_user"):
        data["action"] = "ban"
    elif data.get("mute_user"):
        data["action"] = "mute"
    else:
        data["action"] = "delete"


async def list_keywords(db: AsyncSession, chat_id: int) -> list[KeywordRule]:
    result = await db.execute(
        select(KeywordRule).where(KeywordRule.chat_id == chat_id).order_by(KeywordRule.created_at.desc())
    )
    return list(result.scalars().all())


async def create_keyword(db: AsyncSession, payload: KeywordRuleCreate) -> KeywordRule:
    data = payload.model_dump()
    _apply_legacy_action(data, payload.model_fields_set)
    validate_keyword_actions(data["delete_message"], data["mute_user"], data["ban_user"])
    _sync_legacy_action(data)
    entity = KeywordRule(**data)
    db.add(entity)
    await db.commit()
    await db.refresh(entity)
    return entity


async def update_keyword(
    db: AsyncSession, chat_id: int, keyword_id: int, payload: KeywordRuleUpdate
) -> KeywordRule | None:
    result = await db.execute(
        select(KeywordRule).where(and_(KeywordRule.id == keyword_id, KeywordRule.chat_id == chat_id))
    )
    entity = result.scalar_one_or_none()
    if entity is None:
        return None

    updates = payload.model_dump(exclude_unset=True)
    _apply_legacy_action(updates, payload.model_fields_set)
    merged = {
        "delete_message": entity.delete_message,
        "mute_user": entity.mute_user,
        "ban_user": entity.ban_user,
        **updates,
    }
    validate_keyword_actions(merged["delete_message"], merged["mute_user"], merged["ban_user"])
    _sync_legacy_action(merged)
    updates["action"] = merged["action"]

    for key, value in updates.items():
        setattr(entity, key, value)

    await db.commit()
    await db.refresh(entity)
    return entity


async def delete_keyword(db: AsyncSession, chat_id: int, keyword_id: int) -> bool:
    result = await db.execute(
        select(KeywordRule).where(and_(KeywordRule.id == keyword_id, KeywordRule.chat_id == chat_id))
    )
    entity = result.scalar_one_or_none()
    if entity is None:
        return False

    await db.delete(entity)
    await db.commit()
    return True

