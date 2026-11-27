from aiogram import Bot
from aiogram.utils.token import TokenValidationError
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.db import get_db
from apps.api.app.schemas.community import (
    CommunityConfigRead,
    CommunityConfigUpdate,
    GlobalBanRead,
    GlobalBanWrite,
    NoteRead,
    NoteWrite,
    RssRead,
    RssWrite,
)
from apps.api.app.services import community_feature_service as community
from apps.api.app.services.global_ban_sync import release_global_ban
from apps.api.app.services.runtime_config_service import get_runtime_config

router = APIRouter(prefix="/community", tags=["community"])


@router.get("/global-bans/list", response_model=list[GlobalBanRead])
async def get_global_bans(db: AsyncSession = Depends(get_db)) -> list[GlobalBanRead]:
    return await community.list_global_bans(db)


@router.post("/global-bans", response_model=GlobalBanRead)
async def add_global_ban(payload: GlobalBanWrite, db: AsyncSession = Depends(get_db)) -> GlobalBanRead:
    return await community.add_global_ban(db, payload.user_id, payload.admin_id, payload.reason)


@router.delete("/global-bans/{user_id}")
async def delete_global_ban(user_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    config = await get_runtime_config(db)
    try:
        bot = Bot(token=config.telegram_bot_token) if config.telegram_bot_token else None
    except TokenValidationError:
        bot = None
    try:
        result = await release_global_ban(bot, db, user_id)
    finally:
        if bot:
            await bot.session.close()
    if not result["found"]:
        raise HTTPException(status_code=404, detail="global ban not found")
    return {"ok": not result["failed"], "failed": result["failed"], "legacy_groups": result["legacy_groups"]}


@router.get("/{chat_id}", response_model=CommunityConfigRead)
async def get_community_config(chat_id: int, db: AsyncSession = Depends(get_db)) -> CommunityConfigRead:
    return await _read_community_config(chat_id, db, commit=True)


async def _read_community_config(chat_id: int, db: AsyncSession, *, commit: bool) -> CommunityConfigRead:
    rules = await community.get_rules(db, chat_id)
    welcome = await community.get_welcome_config(db, chat_id, commit=commit)
    warnings = await community.get_warning_setting(db, chat_id, commit=commit)
    reports = await community.get_report_config(db, chat_id, commit=commit)
    locks = await community.get_lock_config(db, chat_id, commit=commit)
    logs = await community.get_log_channel(db, chat_id, commit=commit)
    disabled = await community.list_disabled_commands(db, chat_id)
    return CommunityConfigRead(
        chat_id=chat_id,
        rules_text=rules.rules_text if rules else "",
        welcome_enabled=welcome.welcome_enabled,
        goodbye_enabled=welcome.goodbye_enabled,
        clean_welcome=welcome.clean_welcome,
        welcome_text=welcome.welcome_text,
        goodbye_text=welcome.goodbye_text,
        warn_limit=warnings.warn_limit,
        warn_action=warnings.warn_action,
        warn_mute_minutes=warnings.mute_minutes,
        warn_ban_minutes=warnings.ban_minutes,
        reports_enabled=reports.enabled,
        lock_links=locks.links,
        lock_forwards=locks.forwards,
        lock_media=locks.media,
        lock_stickers=locks.stickers,
        lock_commands=locks.commands,
        log_enabled=logs.enabled,
        log_chat_id=logs.log_chat_id,
        disabled_commands=disabled,
    )


@router.put("/{chat_id}", response_model=CommunityConfigRead)
async def update_community_config(
    chat_id: int,
    payload: CommunityConfigUpdate,
    db: AsyncSession = Depends(get_db),
) -> CommunityConfigRead:
    data = payload.model_dump(exclude_unset=True)
    if any(value is None for value in data.values()):
        raise HTTPException(status_code=422, detail="Community settings cannot be null")

    async with db.begin():
        if "log_enabled" in data or "log_chat_id" in data:
            logs = await community.get_log_channel(db, chat_id, commit=False)
            enabled = data.get("log_enabled", logs.enabled)
            log_chat_id = data.get("log_chat_id", logs.log_chat_id)
            if enabled and not log_chat_id:
                raise HTTPException(status_code=400, detail="log_chat_id is required when log is enabled")
            logs.enabled = enabled
            logs.log_chat_id = log_chat_id if enabled else 0

        if "rules_text" in data:
            if data["rules_text"]:
                await community.set_rules(db, chat_id, data["rules_text"], commit=False)
            else:
                await community.clear_rules(db, chat_id, commit=False)

        field_groups = (
            (community.get_welcome_config, {
                key: key for key in ("welcome_enabled", "goodbye_enabled", "clean_welcome", "welcome_text", "goodbye_text")
            }),
            (community.get_warning_setting, {
                "warn_limit": "warn_limit", "warn_action": "warn_action",
                "warn_mute_minutes": "mute_minutes", "warn_ban_minutes": "ban_minutes",
            }),
            (community.get_report_config, {"reports_enabled": "enabled"}),
            (community.get_lock_config, {f"lock_{key}": key for key in community.LOCK_TYPES}),
        )
        for get_entity, fields in field_groups:
            if fields.keys() & data.keys():
                entity = await get_entity(db, chat_id, commit=False)
                for key, field in fields.items():
                    if key in data:
                        setattr(entity, field, data[key])

        if "disabled_commands" in data:
            current = set(await community.list_disabled_commands(db, chat_id))
            desired = {community.normalize_command(item) for item in data["disabled_commands"]}
            desired &= community.DISABLEABLE_COMMANDS
            for command in current - desired:
                await community.enable_command(db, chat_id, command, commit=False)
            for command in desired - current:
                await community.disable_command(db, chat_id, command, commit=False)

        result = await _read_community_config(chat_id, db, commit=False)
    return result


@router.get("/{chat_id}/notes", response_model=list[NoteRead])
async def get_notes(chat_id: int, db: AsyncSession = Depends(get_db)) -> list[NoteRead]:
    return await community.list_notes(db, chat_id)


@router.post("/{chat_id}/notes", response_model=NoteRead)
async def save_note(chat_id: int, payload: NoteWrite, db: AsyncSession = Depends(get_db)) -> NoteRead:
    return await community.save_note(db, chat_id, payload.name, payload.text, payload.parse_mode)


@router.delete("/{chat_id}/notes/{name}")
async def delete_note(chat_id: int, name: str, db: AsyncSession = Depends(get_db)) -> dict:
    ok = await community.delete_note(db, chat_id, name)
    if not ok:
        raise HTTPException(status_code=404, detail="note not found")
    return {"ok": True}


@router.get("/{chat_id}/rss", response_model=list[RssRead])
async def get_rss(chat_id: int, db: AsyncSession = Depends(get_db)) -> list[RssRead]:
    return await community.list_rss_subscriptions(db, chat_id)


@router.post("/{chat_id}/rss", response_model=RssRead)
async def add_rss(chat_id: int, payload: RssWrite, db: AsyncSession = Depends(get_db)) -> RssRead:
    return await community.add_rss_subscription(db, chat_id, payload.url.strip(), payload.title.strip())


@router.delete("/{chat_id}/rss")
async def delete_rss(chat_id: int, url: str, db: AsyncSession = Depends(get_db)) -> dict:
    ok = await community.remove_rss_subscription(db, chat_id, url)
    if not ok:
        raise HTTPException(status_code=404, detail="rss subscription not found")
    return {"ok": True}

