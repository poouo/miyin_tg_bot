from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.db import get_db
from apps.api.app.schemas.log import ModerationLogRead, ModerationLogWithGroupRead
from apps.api.app.services.log_service import list_logs, list_member_events, list_recent_logs

router = APIRouter(tags=["logs"])


@router.get("/groups/{chat_id}/logs", response_model=list[ModerationLogRead])
async def get_logs(
    chat_id: int,
    limit: int = Query(default=100, ge=1, le=500),
    event_type: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> list[ModerationLogRead]:
    return await list_logs(db, chat_id, limit, event_type)


@router.get("/logs/recent", response_model=list[ModerationLogWithGroupRead])
async def get_recent_logs(
    limit: int = Query(default=200, ge=1, le=500),
    event_type: str | None = Query(default=None),
    chat_id: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> list[ModerationLogWithGroupRead]:
    return await list_recent_logs(db, limit=limit, event_type=event_type, chat_id=chat_id)


@router.get("/logs/member-events", response_model=list[ModerationLogWithGroupRead])
async def get_member_events(
    limit: int = Query(default=200, ge=1, le=500),
    chat_id: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> list[ModerationLogWithGroupRead]:
    return await list_member_events(db, limit=limit, chat_id=chat_id)
