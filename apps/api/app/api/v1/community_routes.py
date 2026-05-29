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

router = APIRouter(prefix="/community", tags=["community"])


@router.get("/global-bans/list", response_model=list[GlobalBanRead])
async def get_global_bans(db: AsyncSession = Depends(get_db)) -> list[GlobalBanRead]:
    return await community.list_global_bans(db)


@router.post("/global-bans", response_model=GlobalBanRead)
async def add_global_ban(payload: GlobalBanWrite, db: AsyncSession = Depends(get_db)) -> GlobalBanRead:
    return await community.add_global_ban(db, payload.user_id, payload.admin_id, payload.reason)


@router.delete("/global-bans/{user_id}")
async def delete_global_ban(user_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    ok = await community.remove_global_ban(db, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="global ban not found")
    return {"ok": True}


@router.get("/{chat_id}", response_model=CommunityConfigRead)
async def get_community_config(chat_id: int, db: AsyncSession = Depends(get_db)) -> CommunityConfigRead:
    rules = await community.get_rules(db, chat_id)
    welcome = await community.get_welcome_config(db, chat_id)
    warnings = await community.get_warning_setting(db, chat_id)
    reports = await community.get_report_config(db, chat_id)
    locks = await community.get_lock_config(db, chat_id)
    logs = await community.get_log_channel(db, chat_id)
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
    if "rules_text" in data:
        if data["rules_text"]:
            await community.set_rules(db, chat_id, data["rules_text"])
        else:
            await community.clear_rules(db, chat_id)

    welcome_keys = {"welcome_enabled", "goodbye_enabled", "clean_welcome", "welcome_text", "goodbye_text"}
    welcome_values = {key: data[key] for key in welcome_keys if key in data}
    if welcome_values:
        await community.update_welcome_config(db, chat_id, **welcome_values)

    if any(key in data for key in ("warn_limit", "warn_action", "warn_mute_minutes", "warn_ban_minutes")):
        current = await community.get_warning_setting(db, chat_id)
        warn_action = data.get("warn_action", current.warn_action)
        warn_minutes = data.get("warn_ban_minutes") if warn_action == "ban" else data.get("warn_mute_minutes")
        await community.update_warning_setting(
            db,
            chat_id,
            warn_limit=data.get("warn_limit"),
            warn_action=data.get("warn_action"),
            minutes=warn_minutes,
        )
        current = await community.get_warning_setting(db, chat_id)
        if "warn_ban_minutes" in data:
            current.ban_minutes = data["warn_ban_minutes"]
        if "warn_mute_minutes" in data:
            current.mute_minutes = data["warn_mute_minutes"]
        await db.commit()

    if "reports_enabled" in data:
        await community.set_reports_enabled(db, chat_id, data["reports_enabled"])

    lock_map = {
        "lock_links": "links",
        "lock_forwards": "forwards",
        "lock_media": "media",
        "lock_stickers": "stickers",
        "lock_commands": "commands",
    }
    for payload_key, lock_key in lock_map.items():
        if payload_key in data:
            await community.set_lock(db, chat_id, lock_key, data[payload_key])

    if "log_enabled" in data or "log_chat_id" in data:
        if data.get("log_enabled") is False:
            await community.unset_log_channel(db, chat_id)
        else:
            log_chat_id = int(data.get("log_chat_id") or 0)
            if log_chat_id:
                await community.set_log_channel(db, chat_id, log_chat_id, True)
            elif data.get("log_enabled"):
                raise HTTPException(status_code=400, detail="log_chat_id is required when log is enabled")

    if "disabled_commands" in data:
        current = set(await community.list_disabled_commands(db, chat_id))
        desired = {community.normalize_command(item) for item in data["disabled_commands"] if item.strip()}
        desired = {item for item in desired if item}
        for command in current - desired:
            await community.enable_command(db, chat_id, command)
        for command in desired - current:
            await community.disable_command(db, chat_id, command)

    return await get_community_config(chat_id, db)


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

