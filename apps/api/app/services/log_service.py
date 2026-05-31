from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.models.entities import GroupConfig, ModerationLog


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


async def list_recent_logs(
    db: AsyncSession,
    limit: int = 200,
    event_type: str | None = None,
    chat_id: int | None = None,
) -> list[dict]:
    stmt = select(ModerationLog, GroupConfig.title).outerjoin(GroupConfig, ModerationLog.chat_id == GroupConfig.chat_id)
    if event_type:
        stmt = stmt.where(ModerationLog.event_type == event_type)
    if chat_id is not None:
        stmt = stmt.where(ModerationLog.chat_id == chat_id)

    result = await db.execute(stmt.order_by(ModerationLog.created_at.desc()).limit(limit))
    items: list[dict] = []
    for log, group_title in result.all():
        items.append(
            {
                "id": log.id,
                "chat_id": log.chat_id,
                "group_title": group_title or "",
                "user_id": log.user_id,
                "username": log.username,
                "event_type": log.event_type,
                "detail": log.detail,
                "created_at": log.created_at,
            }
        )
    return items


async def list_member_events(db: AsyncSession, limit: int = 200, chat_id: int | None = None) -> list[dict]:
    member_event_types = [
        "member_joined",
        "member_left",
        "join_verify_created",
        "join_verify_passed",
        "join_verify_failed",
        "join_verify_timeout",
        "user_kicked",
        "user_banned",
    ]
    stmt = (
        select(ModerationLog, GroupConfig.title)
        .outerjoin(GroupConfig, ModerationLog.chat_id == GroupConfig.chat_id)
        .where(ModerationLog.event_type.in_(member_event_types))
    )
    if chat_id is not None:
        stmt = stmt.where(ModerationLog.chat_id == chat_id)

    result = await db.execute(stmt.order_by(ModerationLog.created_at.desc()).limit(limit))
    items: list[dict] = []
    for log, group_title in result.all():
        items.append(
            {
                "id": log.id,
                "chat_id": log.chat_id,
                "group_title": group_title or "",
                "user_id": log.user_id,
                "username": log.username,
                "event_type": log.event_type,
                "detail": log.detail,
                "created_at": log.created_at,
            }
        )
    return items
