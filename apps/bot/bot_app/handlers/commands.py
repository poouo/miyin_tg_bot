from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from apps.api.app.core.db import SessionLocal
from apps.api.app.services.group_service import ensure_group, get_group
from apps.api.app.services.log_service import add_log
from apps.api.app.services.moderation.join_verification import verify_challenge
from apps.bot.bot_app.state import deepseek_client

router = Router()


@router.message(Command("start"))
async def start_handler(message: Message) -> None:
    await message.reply("Miyin TG Bot 已运行。管理员可在 Web 管理台配置群策略。")


@router.message(Command("ping"))
async def ping_handler(message: Message) -> None:
    await message.reply("pong")


@router.message(Command("ask"))
async def ask_handler(message: Message, command: CommandObject) -> None:
    question = (command.args or "").strip()
    if not question:
        await message.reply("用法: /ask 你的问题")
        return

    chat = message.chat
    async with SessionLocal() as db:
        if chat.type in {"group", "supergroup"}:
            group = await get_group(db, chat.id)
            if group and not group.deepseek_enabled:
                await message.reply("本群已关闭 AI 问答。")
                return
        answer = await deepseek_client.ask(question)
    await message.reply(answer[:3800])


@router.message(Command("verify"))
async def verify_handler(message: Message, command: CommandObject) -> None:
    if message.from_user is None:
        return
    answer = (command.args or "").strip()
    if not answer:
        await message.reply("用法: /verify 你的答案")
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    async with SessionLocal() as db:
        await ensure_group(db, chat_id, message.chat.title or "")
        ok = await verify_challenge(db, chat_id, user_id, answer)
        if ok:
            await message.reply("验证通过，欢迎入群。")
            await add_log(db, chat_id, user_id, message.from_user.username or "", "join_verify_passed", "验证通过")
        else:
            await message.reply("验证失败或已过期，请联系管理员。")

