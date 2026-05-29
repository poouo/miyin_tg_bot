from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.db import get_db
from apps.api.app.schemas.auto_reply import AutoReplyRuleCreate, AutoReplyRuleRead, AutoReplyRuleUpdate
from apps.api.app.services.auto_reply_service import (
    create_auto_reply,
    delete_auto_reply,
    list_auto_replies,
    update_auto_reply,
)

router = APIRouter(prefix="/groups/{chat_id}/auto-replies", tags=["auto-replies"])


@router.get("", response_model=list[AutoReplyRuleRead])
async def get_auto_replies(chat_id: int, db: AsyncSession = Depends(get_db)) -> list[AutoReplyRuleRead]:
    return await list_auto_replies(db, chat_id)


@router.post("", response_model=AutoReplyRuleRead)
async def create_auto_reply_rule(
    chat_id: int, payload: AutoReplyRuleCreate, db: AsyncSession = Depends(get_db)
) -> AutoReplyRuleRead:
    if payload.chat_id != chat_id:
        raise HTTPException(status_code=400, detail="chat_id mismatch")
    return await create_auto_reply(db, payload)


@router.patch("/{rule_id}", response_model=AutoReplyRuleRead)
async def update_auto_reply_rule(
    chat_id: int,
    rule_id: int,
    payload: AutoReplyRuleUpdate,
    db: AsyncSession = Depends(get_db),
) -> AutoReplyRuleRead:
    entity = await update_auto_reply(db, chat_id, rule_id, payload)
    if entity is None:
        raise HTTPException(status_code=404, detail="auto reply rule not found")
    return entity


@router.delete("/{rule_id}")
async def remove_auto_reply_rule(chat_id: int, rule_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    ok = await delete_auto_reply(db, chat_id, rule_id)
    if not ok:
        raise HTTPException(status_code=404, detail="auto reply rule not found")
    return {"ok": True}
