from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.db import get_db
from apps.api.app.schemas.group import GroupConfigCreate, GroupConfigRead, GroupConfigUpdate
from apps.api.app.services.group_service import create_or_update_group, list_groups, patch_group

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("", response_model=list[GroupConfigRead])
async def get_groups(db: AsyncSession = Depends(get_db)) -> list[GroupConfigRead]:
    return await list_groups(db)


@router.post("", response_model=GroupConfigRead)
async def upsert_group(payload: GroupConfigCreate, db: AsyncSession = Depends(get_db)) -> GroupConfigRead:
    return await create_or_update_group(db, payload)


@router.patch("/{chat_id}", response_model=GroupConfigRead)
async def update_group(chat_id: int, payload: GroupConfigUpdate, db: AsyncSession = Depends(get_db)) -> GroupConfigRead:
    entity = await patch_group(db, chat_id, payload)
    if entity is None:
        raise HTTPException(status_code=404, detail="group not found")
    return entity

