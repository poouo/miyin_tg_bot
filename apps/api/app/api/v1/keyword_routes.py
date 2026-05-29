from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.db import get_db
from apps.api.app.schemas.keyword import KeywordRuleCreate, KeywordRuleRead, KeywordRuleUpdate
from apps.api.app.services.keyword_service import create_keyword, delete_keyword, list_keywords, update_keyword

router = APIRouter(prefix="/groups/{chat_id}/keywords", tags=["keywords"])


@router.get("", response_model=list[KeywordRuleRead])
async def get_keyword_rules(chat_id: int, db: AsyncSession = Depends(get_db)) -> list[KeywordRuleRead]:
    return await list_keywords(db, chat_id)


@router.post("", response_model=KeywordRuleRead)
async def create_keyword_rule(chat_id: int, payload: KeywordRuleCreate, db: AsyncSession = Depends(get_db)) -> KeywordRuleRead:
    if payload.chat_id != chat_id:
        raise HTTPException(status_code=400, detail="chat_id mismatch")
    return await create_keyword(db, payload)


@router.patch("/{keyword_id}", response_model=KeywordRuleRead)
async def update_keyword_rule(
    chat_id: int,
    keyword_id: int,
    payload: KeywordRuleUpdate,
    db: AsyncSession = Depends(get_db),
) -> KeywordRuleRead:
    entity = await update_keyword(db, chat_id, keyword_id, payload)
    if entity is None:
        raise HTTPException(status_code=404, detail="keyword rule not found")
    return entity


@router.delete("/{keyword_id}")
async def remove_keyword_rule(chat_id: int, keyword_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    ok = await delete_keyword(db, chat_id, keyword_id)
    if not ok:
        raise HTTPException(status_code=404, detail="keyword rule not found")
    return {"ok": True}

