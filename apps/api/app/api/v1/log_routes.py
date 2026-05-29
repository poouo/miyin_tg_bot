from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.db import get_db
from apps.api.app.schemas.log import ModerationLogRead
from apps.api.app.services.log_service import list_logs

router = APIRouter(prefix="/groups/{chat_id}/logs", tags=["logs"])


@router.get("", response_model=list[ModerationLogRead])
async def get_logs(
    chat_id: int,
    limit: int = Query(default=100, ge=1, le=500),
    event_type: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> list[ModerationLogRead]:
    return await list_logs(db, chat_id, limit, event_type)

