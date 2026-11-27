import asyncio
import logging
from datetime import datetime, timedelta, timezone
from weakref import WeakValueDictionary

from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.models.entities import GlobalBan, ModerationLog, UserSanction
from apps.api.app.services.community_feature_service import remove_global_ban
from apps.api.app.services.moderation.auto_recover import GLOBAL_BAN_REASON, add_ban_sanction, mark_recovered

logger = logging.getLogger(__name__)
_user_locks: WeakValueDictionary[int, asyncio.Lock] = WeakValueDictionary()


async def _global_ban_entries(db: AsyncSession, user_id: int) -> list[UserSanction]:
    result = await db.scalars(select(UserSanction).where(
        UserSanction.user_id == user_id,
        UserSanction.sanction_type == "ban",
        UserSanction.reason == GLOBAL_BAN_REASON,
        UserSanction.recovered.is_(False),
    ))
    return list(result)


async def apply_global_ban(bot: Bot, db: AsyncSession, chat_id: int, user_id: int) -> None:
    async with _user_locks.setdefault(user_id, asyncio.Lock()):
        if not await db.scalar(select(GlobalBan.active).where(GlobalBan.user_id == user_id)):
            return
        if await bot.ban_chat_member(chat_id, user_id) is False:
            raise RuntimeError("Telegram rejected the global ban")
        if not any(item.chat_id == chat_id for item in await _global_ban_entries(db, user_id)):
            await add_ban_sanction(db, chat_id, user_id, GLOBAL_BAN_REASON, None)


async def release_global_ban(bot: Bot | None, db: AsyncSession, user_id: int) -> dict:
    async with _user_locks.setdefault(user_id, asyncio.Lock()):
        return await _release_global_ban(bot, db, user_id)


async def _release_global_ban(bot: Bot | None, db: AsyncSession, user_id: int) -> dict:
    removed = await remove_global_ban(db, user_id)
    tracked = select(UserSanction.chat_id).where(
        UserSanction.user_id == user_id,
        UserSanction.sanction_type == "ban",
        UserSanction.reason == GLOBAL_BAN_REASON,
    )
    legacy_groups = list(await db.scalars(select(ModerationLog.chat_id).where(
        ModerationLog.user_id == user_id,
        ModerationLog.event_type.in_(("global_ban", "global_ban_enforced")),
        ModerationLog.chat_id < 0,
        ModerationLog.chat_id.not_in(tracked),
    ).distinct())) if removed else []
    entries = await _global_ban_entries(db, user_id)
    if not entries:
        return {"found": removed, "failed": [], "legacy_groups": legacy_groups}

    entry_ids = {}
    for item in entries:
        entry_ids.setdefault(item.chat_id, []).append(item.id)
    failed = []
    now = datetime.now(timezone.utc)
    for chat_id, ids in entry_ids.items():
        try:
            if bot is None:
                raise RuntimeError("Telegram bot token is not configured")
            local_bans = await db.scalars(select(UserSanction.expires_at).where(
                UserSanction.chat_id == chat_id,
                UserSanction.user_id == user_id,
                UserSanction.sanction_type == "ban",
                UserSanction.reason != GLOBAL_BAN_REASON,
                UserSanction.recovered.is_(False),
            ))
            expirations = [
                end if end is None or end.tzinfo else end.replace(tzinfo=timezone.utc)
                for end in local_bans
            ]
            if None not in expirations:
                end = max(expirations, default=now)
                if end > now:
                    # Reapply the local ban without turning a short remaining duration into a permanent ban.
                    result = await bot.ban_chat_member(chat_id, user_id, until_date=max(end, now + timedelta(seconds=31)))
                else:
                    result = await bot.unban_chat_member(chat_id, user_id, only_if_banned=True)
                if result is False:
                    raise RuntimeError("Telegram rejected the restriction update")
            for entry_id in ids:
                await mark_recovered(db, entry_id)
        except Exception:
            await db.rollback()
            logger.exception("Could not release global ban in chat %s", chat_id)
            failed.append(chat_id)
    return {"found": True, "failed": failed, "legacy_groups": legacy_groups}
