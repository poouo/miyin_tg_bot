from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.db import get_db
from apps.api.app.schemas.ad_keyword import (
    AdKeywordCreate,
    AdKeywordRead,
    AdKeywordTemplateApply,
    AdKeywordTemplateApplyResult,
    AdKeywordTemplateRead,
    AdKeywordUpdate,
)
from apps.api.app.services.ad_keyword_service import create_ad_keyword, delete_ad_keyword, list_ad_keywords, update_ad_keyword
from apps.api.app.services.ad_keyword_templates import apply_templates, describe_templates

router = APIRouter(prefix="/groups/{chat_id}/ad-keywords", tags=["ad-keywords"])


@router.get("", response_model=list[AdKeywordRead])
async def get_ad_keywords(chat_id: int, db: AsyncSession = Depends(get_db)) -> list[AdKeywordRead]:
    return await list_ad_keywords(db, chat_id)


@router.get("/templates", response_model=list[AdKeywordTemplateRead])
async def get_ad_keyword_templates(chat_id: int, db: AsyncSession = Depends(get_db)) -> list[AdKeywordTemplateRead]:
    return await describe_templates(db, chat_id)


@router.post("/templates/apply", response_model=AdKeywordTemplateApplyResult)
async def apply_ad_keyword_templates(
    chat_id: int,
    payload: AdKeywordTemplateApply,
    db: AsyncSession = Depends(get_db),
) -> AdKeywordTemplateApplyResult:
    try:
        return await apply_templates(
            db,
            chat_id,
            payload.template_ids,
            delete_message=payload.delete_message,
            mute_user=payload.mute_user,
            mute_minutes=payload.mute_minutes,
            ban_user=payload.ban_user,
            ban_minutes=payload.ban_minutes,
            apply_to_mentions=payload.apply_to_mentions,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("", response_model=AdKeywordRead)
async def create_ad_keyword_rule(chat_id: int, payload: AdKeywordCreate, db: AsyncSession = Depends(get_db)) -> AdKeywordRead:
    if payload.chat_id != chat_id:
        raise HTTPException(status_code=400, detail="chat_id mismatch")
    return await create_ad_keyword(db, payload)


@router.patch("/{keyword_id}", response_model=AdKeywordRead)
async def update_ad_keyword_rule(
    chat_id: int,
    keyword_id: int,
    payload: AdKeywordUpdate,
    db: AsyncSession = Depends(get_db),
) -> AdKeywordRead:
    try:
        entity = await update_ad_keyword(db, chat_id, keyword_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if entity is None:
        raise HTTPException(status_code=404, detail="ad keyword not found")
    return entity


@router.delete("/{keyword_id}")
async def remove_ad_keyword_rule(chat_id: int, keyword_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    ok = await delete_ad_keyword(db, chat_id, keyword_id)
    if not ok:
        raise HTTPException(status_code=404, detail="ad keyword not found")
    return {"ok": True}
