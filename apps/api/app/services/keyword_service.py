from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.models.entities import KeywordRule
from apps.api.app.schemas.keyword import KeywordRuleCreate, KeywordRuleUpdate


async def list_keywords(db: AsyncSession, chat_id: int) -> list[KeywordRule]:
    result = await db.execute(
        select(KeywordRule).where(KeywordRule.chat_id == chat_id).order_by(KeywordRule.created_at.desc())
    )
    return list(result.scalars().all())


async def create_keyword(db: AsyncSession, payload: KeywordRuleCreate) -> KeywordRule:
    entity = KeywordRule(**payload.model_dump())
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

    for key, value in payload.model_dump(exclude_unset=True).items():
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

