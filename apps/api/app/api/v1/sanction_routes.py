from aiogram import Bot
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.db import get_db
from apps.api.app.schemas.sanction import BanSanctionRead
from apps.api.app.services.group_service import get_group
from apps.api.app.services.log_service import add_log
from apps.api.app.services.moderation.auto_recover import list_active_ban_sanctions, mark_ban_recovered
from apps.api.app.services.runtime_config_service import get_runtime_config

router = APIRouter(prefix="/sanctions", tags=["sanctions"])


@router.get("/bans", response_model=list[BanSanctionRead])
async def list_bans(chat_id: int | None = None, db: AsyncSession = Depends(get_db)) -> list[BanSanctionRead]:
    items = await list_active_ban_sanctions(db, chat_id)
    result: list[BanSanctionRead] = []
    title_cache: dict[int, str] = {}
    for item in items:
        if item.chat_id not in title_cache:
            group = await get_group(db, item.chat_id)
            title_cache[item.chat_id] = group.title if group else ""
        result.append(
            BanSanctionRead(
                id=item.id,
                chat_id=item.chat_id,
                group_title=title_cache[item.chat_id],
                user_id=item.user_id,
                reason=item.reason,
                expires_at=item.expires_at,
                created_at=item.created_at,
            )
        )
    return result


@router.post("/bans/{chat_id}/{user_id}/unban")
async def unban_user(chat_id: int, user_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    runtime = await get_runtime_config(db)
    token = runtime.telegram_bot_token.strip()
    if not token:
        raise HTTPException(status_code=400, detail="telegram bot token is not configured")

    bot = Bot(token=token)
    try:
        await bot.unban_chat_member(chat_id, user_id, only_if_banned=True)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"telegram unban failed: {exc}") from exc
    finally:
        await bot.session.close()

    await mark_ban_recovered(db, chat_id, user_id)
    await add_log(db, chat_id, user_id, "", "manual_unban", "web_admin")
    return {"ok": True}
