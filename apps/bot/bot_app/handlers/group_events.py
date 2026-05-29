from datetime import datetime, timedelta, timezone

from aiogram import F, Router
from aiogram.types import ChatPermissions, Message

from apps.api.app.core.db import SessionLocal
from apps.api.app.services.group_service import ensure_group
from apps.api.app.services.log_service import add_log
from apps.api.app.services.moderation.auto_recover import add_mute_sanction
from apps.api.app.services.moderation.join_verification import create_challenge
from apps.api.app.services.runtime_config_service import get_runtime_config
from apps.bot.bot_app.state import deepseek_client, policy_engine

router = Router()


@router.message(F.chat.type.in_({"group", "supergroup"}), F.new_chat_members)
async def new_member_handler(message: Message) -> None:
    chat = message.chat
    if not message.new_chat_members:
        return

    async with SessionLocal() as db:
        runtime = await get_runtime_config(db)
        group = await ensure_group(db, chat.id, chat.title or "")
        if not group.join_verification_enabled:
            return

        for member in message.new_chat_members:
            if member.is_bot:
                continue
            await message.bot.restrict_chat_member(
                chat_id=chat.id,
                user_id=member.id,
                permissions=ChatPermissions(can_send_messages=False),
            )
            challenge = await create_challenge(db, chat.id, member.id)
            await message.answer(
                f"欢迎 {member.full_name}，请在 {runtime.join_verify_timeout_sec} 秒内完成验证:\n"
                f"`{challenge.question}`\n"
                "回复命令: /verify 你的答案",
                parse_mode="Markdown",
            )
            await add_log(db, chat.id, member.id, member.username or "", "join_verify_created", challenge.question)


@router.message(F.chat.type.in_({"group", "supergroup"}), F.text)
async def group_text_handler(message: Message) -> None:
    if message.from_user is None or message.from_user.is_bot:
        return
    text = message.text or ""
    chat = message.chat
    user = message.from_user

    async with SessionLocal() as db:
        runtime = await get_runtime_config(db)
        group = await ensure_group(db, chat.id, chat.title or "")
        decision = await policy_engine.check_message(db, chat.id, user.id, text)
        if decision.blocked:
            try:
                await message.delete()
            except Exception:
                pass

            mute_minutes = 10
            reason = decision.reason
            if decision.keyword_rule and decision.keyword_rule.action == "mute":
                mute_minutes = decision.keyword_rule.mute_minutes
                reason = f"{reason}:{decision.keyword_rule.keyword}"
            elif decision.reason in {"ad_block", "anti_spam"}:
                mute_minutes = 30

            if decision.reason in {"ad_block", "anti_spam"} or (
                decision.keyword_rule and decision.keyword_rule.action == "mute"
            ):
                await message.bot.restrict_chat_member(
                    chat_id=chat.id,
                    user_id=user.id,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=datetime.now(timezone.utc) + timedelta(minutes=mute_minutes),
                )
                await add_mute_sanction(db, chat.id, user.id, reason, mute_minutes)

            await add_log(db, chat.id, user.id, user.username or "", "message_blocked", reason)
            return

        bot_mention = runtime.telegram_bot_username.strip()
        has_mention = bool(bot_mention) and f"@{bot_mention.lower()}" in text.lower()
        if group.deepseek_enabled and (has_mention or text.startswith("问:")):
            question = text.replace(f"@{bot_mention}", "").strip() if bot_mention else text.strip()
            if question.startswith("问:"):
                question = question[2:].strip()
            if question:
                answer = await deepseek_client.ask(question, db=db)
                await message.reply(answer[:3800])
