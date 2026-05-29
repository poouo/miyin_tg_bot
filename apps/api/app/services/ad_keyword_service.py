from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.models.entities import AdKeyword
from apps.api.app.schemas.ad_keyword import AdKeywordCreate, AdKeywordUpdate


async def list_ad_keywords(db: AsyncSession, chat_id: int) -> list[AdKeyword]:
    result = await db.execute(select(AdKeyword).where(AdKeyword.chat_id == chat_id).order_by(AdKeyword.created_at.desc()))
    return list(result.scalars().all())


async def create_ad_keyword(db: AsyncSession, payload: AdKeywordCreate) -> AdKeyword:
    entity = AdKeyword(**payload.model_dump())
    db.add(entity)
    try:
        await db.commit()
        await db.refresh(entity)
        return entity
    except IntegrityError:
        await db.rollback()
        result = await db.execute(
            select(AdKeyword).where(and_(AdKeyword.chat_id == payload.chat_id, AdKeyword.keyword == payload.keyword))
        )
        existing = result.scalar_one_or_none()
        if existing is None:
            raise
        return existing


async def update_ad_keyword(
    db: AsyncSession, chat_id: int, keyword_id: int, payload: AdKeywordUpdate
) -> AdKeyword | None:
    result = await db.execute(
        select(AdKeyword).where(and_(AdKeyword.id == keyword_id, AdKeyword.chat_id == chat_id))
    )
    entity = result.scalar_one_or_none()
    if entity is None:
        return None

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(entity, key, value)

    await db.commit()
    await db.refresh(entity)
    return entity


async def delete_ad_keyword(db: AsyncSession, chat_id: int, keyword_id: int) -> bool:
    result = await db.execute(
        select(AdKeyword).where(and_(AdKeyword.id == keyword_id, AdKeyword.chat_id == chat_id))
    )
    entity = result.scalar_one_or_none()
    if entity is None:
        return False

    await db.delete(entity)
    await db.commit()
    return True


async def match_ad_keyword(db: AsyncSession, chat_id: int, text: str) -> AdKeyword | None:
    content = (text or "").strip().lower()
    if not content:
        return None

    rules = await list_ad_keywords(db, chat_id)
    for rule in rules:
        if not rule.enabled:
            continue
        if rule.keyword.strip().lower() in content:
            return rule
    return None
