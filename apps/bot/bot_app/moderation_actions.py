from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from aiogram import Bot
from aiogram.types import ChatPermissions
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.services.log_service import add_log
from apps.api.app.services.moderation.auto_recover import add_mute_sanction


@dataclass(frozen=True)
class ModerationActionConfig:
    action: str
    mute_minutes: int
    ban_minutes: int


def _until_minutes(minutes: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)


async def apply_moderation_action(
    bot: Bot,
    db: AsyncSession,
    chat_id: int,
    user_id: int,
    username: str,
    reason: str,
    config: ModerationActionConfig,
) -> None:
    action = config.action
    if action == "kick":
        until = datetime.now(timezone.utc) + timedelta(seconds=45)
        await bot.ban_chat_member(chat_id, user_id, until_date=until)
        await bot.unban_chat_member(chat_id, user_id, only_if_banned=True)
        await add_log(db, chat_id, user_id, username, "user_kicked", reason)
        return

    if action == "ban":
        await bot.ban_chat_member(chat_id, user_id, until_date=_until_minutes(config.ban_minutes))
        await add_log(db, chat_id, user_id, username, "user_banned", f"{reason}:{config.ban_minutes}m")
        return

    await bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=ChatPermissions(can_send_messages=False),
        until_date=_until_minutes(config.mute_minutes),
    )
    await add_mute_sanction(db, chat_id, user_id, reason, config.mute_minutes)
    await add_log(db, chat_id, user_id, username, "user_muted", f"{reason}:{config.mute_minutes}m")
