from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.models.entities import ChatUserIdentity, ModerationLog


def normalize_username(username: str | None) -> str:
    return (username or "").strip().lstrip("@").lower()


async def record_chat_user_identity(
    db: AsyncSession,
    chat_id: int,
    user_id: int,
    username: str | None,
) -> ChatUserIdentity:
    result = await db.execute(
        select(ChatUserIdentity).where(
            and_(ChatUserIdentity.chat_id == chat_id, ChatUserIdentity.user_id == user_id)
        )
    )
    entity = result.scalar_one_or_none()
    normalized_username = normalize_username(username)
    if entity is None:
        entity = ChatUserIdentity(chat_id=chat_id, user_id=user_id, username=normalized_username)
        db.add(entity)
        try:
            await db.commit()
            await db.refresh(entity)
            return entity
        except IntegrityError:
            await db.rollback()
            result = await db.execute(
                select(ChatUserIdentity).where(
                    and_(ChatUserIdentity.chat_id == chat_id, ChatUserIdentity.user_id == user_id)
                )
            )
            entity = result.scalar_one()

    if entity.username == normalized_username:
        return entity

    entity.username = normalized_username
    await db.commit()
    await db.refresh(entity)
    return entity


async def find_chat_user_ids_by_username(
    db: AsyncSession,
    chat_id: int,
    username: str,
) -> list[int]:
    normalized_username = normalize_username(username)
    if not normalized_username:
        return []

    result = await db.execute(
        select(ChatUserIdentity.user_id)
        .where(
            and_(
                ChatUserIdentity.chat_id == chat_id,
                ChatUserIdentity.username == normalized_username,
            )
        )
        .order_by(ChatUserIdentity.updated_at.desc())
        .limit(5)
    )
    user_ids = list(result.scalars().all())

    log_result = await db.execute(
        select(ModerationLog.user_id)
        .where(
            and_(
                ModerationLog.chat_id == chat_id,
                func.lower(ModerationLog.username) == normalized_username,
                ModerationLog.user_id > 0,
            )
        )
        .order_by(ModerationLog.created_at.desc())
        .limit(5)
    )
    for user_id in log_result.scalars().all():
        if user_id not in user_ids:
            user_ids.append(user_id)
    return user_ids[:5]
