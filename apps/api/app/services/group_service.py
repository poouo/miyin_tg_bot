from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.models.entities import GroupConfig
from apps.api.app.schemas.group import GroupConfigCreate, GroupConfigUpdate


async def list_groups(db: AsyncSession) -> list[GroupConfig]:
    result = await db.execute(select(GroupConfig).order_by(GroupConfig.created_at.desc()))
    return list(result.scalars().all())


async def get_group(db: AsyncSession, chat_id: int) -> GroupConfig | None:
    result = await db.execute(select(GroupConfig).where(GroupConfig.chat_id == chat_id))
    return result.scalar_one_or_none()


async def create_or_update_group(db: AsyncSession, payload: GroupConfigCreate) -> GroupConfig:
    entity = await get_group(db, payload.chat_id)
    if entity is None:
        entity = GroupConfig(**payload.model_dump())
        db.add(entity)
    else:
        for key, value in payload.model_dump().items():
            setattr(entity, key, value)

    await db.commit()
    await db.refresh(entity)
    return entity


async def patch_group(db: AsyncSession, chat_id: int, payload: GroupConfigUpdate) -> GroupConfig | None:
    entity = await get_group(db, chat_id)
    if entity is None:
        return None

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(entity, key, value)

    await db.commit()
    await db.refresh(entity)
    return entity


async def ensure_group(db: AsyncSession, chat_id: int, title: str = "") -> GroupConfig:
    entity = await get_group(db, chat_id)
    if entity is not None:
        if title and entity.title != title:
            entity.title = title
            await db.commit()
            await db.refresh(entity)
        return entity

    payload = GroupConfigCreate(chat_id=chat_id, title=title or "")
    return await create_or_update_group(db, payload)
