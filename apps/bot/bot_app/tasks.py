import asyncio

from aiogram import Bot
from aiogram.types import ChatPermissions

from apps.api.app.core.db import SessionLocal
from apps.api.app.services.log_service import add_log
from apps.api.app.services.moderation.auto_recover import list_recoverable_sanctions, mark_recovered
from apps.api.app.services.moderation.join_verification import list_expired_unpassed
from apps.api.app.services.runtime_config_service import get_runtime_config
from apps.bot.bot_app.moderation_actions import ModerationActionConfig, apply_moderation_action


async def recover_mute_task(bot: Bot) -> None:
    while True:
        try:
            async with SessionLocal() as db:
                sanctions = await list_recoverable_sanctions(db)
                for item in sanctions:
                    await bot.restrict_chat_member(
                        chat_id=item.chat_id,
                        user_id=item.user_id,
                        permissions=ChatPermissions(can_send_messages=True),
                    )
                    await mark_recovered(db, item.id)
                    await add_log(db, item.chat_id, item.user_id, "", "auto_recover", item.reason)
        except Exception:
            pass
        await asyncio.sleep(20)


async def kick_unverified_task(bot: Bot) -> None:
    while True:
        try:
            async with SessionLocal() as db:
                runtime = await get_runtime_config(db)
                items = await list_expired_unpassed(db)
                for challenge in items:
                    action_config = ModerationActionConfig(
                        action=runtime.join_verify_fail_action,
                        mute_minutes=runtime.join_verify_fail_mute_minutes,
                        ban_minutes=runtime.join_verify_fail_ban_minutes,
                    )
                    await apply_moderation_action(
                        bot,
                        db,
                        challenge.chat_id,
                        challenge.user_id,
                        "",
                        "join_verify_timeout",
                        action_config,
                    )
                    await add_log(
                        db,
                        challenge.chat_id,
                        challenge.user_id,
                        "",
                        "join_verify_timeout",
                        f"join verification timed out, action={action_config.action}",
                    )
                    challenge.passed = True
                await db.commit()
        except Exception:
            pass
        await asyncio.sleep(15)
