from dataclasses import dataclass
from datetime import datetime, timezone

from aiogram import Bot
from aiogram.types import ChatPermissions
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.services.log_service import add_log
from apps.api.app.services.moderation.auto_recover import add_mute_sanction

DEFAULT_KICK_MINUTES = 1


@dataclass(frozen=True)
class ModerationActionConfig:
    action: str
    kick_minutes: int
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
        kick_minutes = max(1, int(config.kick_minutes or 1))
        until = _until_minutes(kick_minutes)
        await bot.ban_chat_member(chat_id, user_id, until_date=until)
        await add_log(db, chat_id, user_id, username, "user_kicked", f"{reason}:{kick_minutes}m")
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
