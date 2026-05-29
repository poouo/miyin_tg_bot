import asyncio
from datetime import datetime, timedelta, timezone

from aiogram import Bot
from aiogram.types import ChatPermissions

from apps.api.app.core.db import SessionLocal
from apps.api.app.services.log_service import add_log
from apps.api.app.services.moderation.auto_recover import list_recoverable_sanctions, mark_recovered
from apps.api.app.services.moderation.join_verification import list_expired_unpassed


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
                items = await list_expired_unpassed(db)
                for challenge in items:
                    until = datetime.now(timezone.utc) + timedelta(seconds=45)
                    await bot.ban_chat_member(challenge.chat_id, challenge.user_id, until_date=until)
                    await bot.unban_chat_member(challenge.chat_id, challenge.user_id, only_if_banned=True)
                    await add_log(
                        db,
                        challenge.chat_id,
                        challenge.user_id,
                        "",
                        "join_verify_timeout",
                        "join verification timed out, user removed",
                    )
                    challenge.passed = True
                await db.commit()
        except Exception:
            pass
        await asyncio.sleep(15)
