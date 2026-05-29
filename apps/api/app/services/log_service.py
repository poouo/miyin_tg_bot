from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.models.entities import ModerationLog


async def add_log(
    db: AsyncSession,
    chat_id: int,
    user_id: int,
    username: str,
    event_type: str,
    detail: str,
) -> ModerationLog:
    entity = ModerationLog(
        chat_id=chat_id,
        user_id=user_id,
        username=username,
        event_type=event_type,
        detail=detail,
    )
    db.add(entity)
    await db.commit()
    await db.refresh(entity)
    return entity


async def list_logs(db: AsyncSession, chat_id: int, limit: int = 100, event_type: str | None = None) -> list[ModerationLog]:
    stmt = select(ModerationLog).where(ModerationLog.chat_id == chat_id)
    if event_type:
        stmt = stmt.where(and_(ModerationLog.chat_id == chat_id, ModerationLog.event_type == event_type))
    result = await db.execute(stmt.order_by(ModerationLog.created_at.desc()).limit(limit))
    return list(result.scalars().all())

