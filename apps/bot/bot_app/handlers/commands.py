from datetime import datetime, timedelta, timezone

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import ChatPermissions, Message

from apps.api.app.core.db import SessionLocal
from apps.api.app.services.group_service import ensure_group, get_group
from apps.api.app.services.log_service import add_log
from apps.api.app.services.moderation.join_verification import get_challenge, verify_challenge
from apps.bot.bot_app.ai_formatting import reply_ai_text
from apps.bot.bot_app.moderation_actions import DEFAULT_KICK_MINUTES, ModerationActionConfig, apply_moderation_action
from apps.bot.bot_app.state import deepseek_client
from apps.bot.bot_app.verification_notices import send_temporary_notice, send_verify_fail_notice, send_verify_pass_notice

router = Router()
MANAGER_ROLES = {"administrator", "creator"}
MEMBER_UNRESTRICT_PERMISSIONS = ChatPermissions(
    can_send_messages=True,
    can_send_audios=True,
    can_send_documents=True,
    can_send_photos=True,
    can_send_videos=True,
    can_send_video_notes=True,
    can_send_voice_notes=True,
    can_send_polls=True,
    can_send_other_messages=True,
    can_add_web_page_previews=True,
    can_invite_users=True,
)
USER_HELP_TEXT = "\n".join(
    [
        "<b>可用指令</b>",
        "<code>/ping</code> - 检查机器人状态",
        "<code>/ask 问题</code> - 与 AI 聊天",
        "<code>/verify 答案</code> - 完成入群验证",
    ]
)
ADMIN_HELP_TEXT = "\n".join(
    [
        USER_HELP_TEXT,
        "",
        "<b>管理员指令</b>",
        "<code>/ban 用户ID 分钟</code> - 拉黑用户",
        "<code>/unban 用户ID</code> - 解除拉黑",
        "<code>/kick 用户ID 分钟</code> - 移除并限制重新加入",
        "<code>/mute 用户ID 分钟</code> - 禁言用户",
        "<code>/unmute 用户ID</code> - 解除禁言",
        "<i>提示：管理员指令也支持回复用户消息后使用。</i>",
    ]
)
ADMIN_ONLY_TEXT = "<b>权限不足</b>\n此指令仅群管理员可用。"


async def is_group_manager(message: Message) -> bool:
    if message.from_user is None:
        return False
    if message.chat.type not in {"group", "supergroup"}:
        return False
    try:
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
    except Exception:
        return False
    return getattr(member, "status", "") in MANAGER_ROLES


async def register_group_if_needed(message: Message) -> None:
    if message.chat.type not in {"group", "supergroup"}:
        return
    async with SessionLocal() as db:
        await ensure_group(db, message.chat.id, message.chat.title or "")


def parse_target_user_id(message: Message, command: CommandObject) -> int | None:
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user.id

    args = (command.args or "").strip()
    if not args:
        return None
    try:
        return int(args.split()[0])
    except ValueError:
        return None


def parse_minutes(command: CommandObject, default_minutes: int) -> int:
    args = (command.args or "").strip()
    if not args:
        return default_minutes

    parts = args.split()
    candidates = parts[1:] if len(parts) > 1 else parts
    for item in candidates:
        try:
            minutes = int(item)
            return max(1, min(minutes, 10080))
        except ValueError:
            continue
    return default_minutes


@router.message(Command("start"))
async def start_handler(message: Message) -> None:
    await register_group_if_needed(message)
    await message.reply("Miyin TG Bot is running.")


@router.message(Command("ping"))
async def ping_handler(message: Message) -> None:
    await register_group_if_needed(message)
    await message.reply("pong")


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    await register_group_if_needed(message)
    if await is_group_manager(message):
        await message.reply(ADMIN_HELP_TEXT, parse_mode="HTML")
        return
    await message.reply(USER_HELP_TEXT, parse_mode="HTML")


async def require_group_manager(message: Message) -> bool:
    if await is_group_manager(message):
        return True
    await message.reply(ADMIN_ONLY_TEXT, parse_mode="HTML")
    return False


@router.message(Command("ask"))
async def ask_handler(message: Message, command: CommandObject) -> None:
    question = (command.args or "").strip()
    if not question:
        await message.reply("Usage: /ask your question")
        return

    chat = message.chat
    async with SessionLocal() as db:
        if chat.type in {"group", "supergroup"}:
            await ensure_group(db, chat.id, chat.title or "")
            group = await get_group(db, chat.id)
            if group and not group.deepseek_enabled:
                await message.reply("AI is disabled in this group.")
                return
        answer = await deepseek_client.ask(question, db=db)
    await reply_ai_text(message, answer)


@router.message(Command("verify"))
async def verify_handler(message: Message, command: CommandObject) -> None:
    if message.from_user is None:
        return
    answer = (command.args or "").strip()
    if not answer:
        await message.reply("请点击入群验证消息下方按钮，或使用 /verify 你的答案")
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    async with SessionLocal() as db:
        group = await ensure_group(db, chat_id, message.chat.title or "")
        ok = await verify_challenge(db, chat_id, user_id, answer)
        if ok:
            await message.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=MEMBER_UNRESTRICT_PERMISSIONS,
            )
            await add_log(db, chat_id, user_id, message.from_user.username or "", "join_verify_passed", "ok")
            await send_verify_pass_notice(
                message.bot,
                chat_id,
                user_id,
                message.from_user.full_name,
                message.from_user.username or "",
            )
        else:
            challenge = await get_challenge(db, chat_id, user_id)
            if challenge is not None and not challenge.passed:
                action_config = ModerationActionConfig(
                    action=group.join_verify_fail_action,
                    kick_minutes=group.join_verify_fail_kick_minutes,
                    mute_minutes=group.join_verify_fail_mute_minutes,
                    ban_minutes=group.join_verify_fail_ban_minutes,
                )
                await apply_moderation_action(
                    message.bot,
                    db,
                    chat_id,
                    user_id,
                    message.from_user.username or "",
                    "join_verify_failed",
                    action_config,
                )
                await send_verify_fail_notice(
                    message.bot,
                    chat_id,
                    user_id,
                    action_config.action,
                    action_config.kick_minutes,
                    action_config.mute_minutes,
                    action_config.ban_minutes,
                    message.from_user.full_name,
                    message.from_user.username or "",
                    "未通过验证",
                )
                challenge.passed = True
                await db.commit()
            else:
                await send_temporary_notice(message.bot, chat_id, "验证失败或已过期。")
            await add_log(db, chat_id, user_id, message.from_user.username or "", "join_verify_failed", "command")


@router.message(Command("ban"))
async def ban_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    if message.from_user is None:
        return

    target_user_id = parse_target_user_id(message, command)
    if target_user_id is None:
        await message.reply("Usage: reply + /ban [minutes], or /ban user_id [minutes]")
        return

    minutes = parse_minutes(command, 1440)
    until_date = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    await message.bot.ban_chat_member(message.chat.id, target_user_id, until_date=until_date)

    async with SessionLocal() as db:
        await add_log(
            db,
            message.chat.id,
            message.from_user.id,
            message.from_user.username or "",
            "manual_ban",
            f"target={target_user_id}, minutes={minutes}",
        )
    await message.reply(f"User {target_user_id} banned for {minutes} minutes.")


@router.message(Command("unban"))
async def unban_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    if message.from_user is None:
        return

    target_user_id = parse_target_user_id(message, command)
    if target_user_id is None:
        await message.reply("Usage: reply + /unban, or /unban user_id")
        return

    await message.bot.unban_chat_member(message.chat.id, target_user_id, only_if_banned=True)
    async with SessionLocal() as db:
        await add_log(
            db,
            message.chat.id,
            message.from_user.id,
            message.from_user.username or "",
            "manual_unban",
            f"target={target_user_id}",
        )
    await message.reply(f"User {target_user_id} unbanned.")


@router.message(Command("kick"))
async def kick_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    if message.from_user is None:
        return

    target_user_id = parse_target_user_id(message, command)
    if target_user_id is None:
        await message.reply("Usage: reply + /kick [minutes], or /kick user_id [minutes]")
        return

    minutes = parse_minutes(command, DEFAULT_KICK_MINUTES)
    until_date = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    await message.bot.ban_chat_member(message.chat.id, target_user_id, until_date=until_date)
    async with SessionLocal() as db:
        await add_log(
            db,
            message.chat.id,
            message.from_user.id,
            message.from_user.username or "",
            "manual_kick",
            f"target={target_user_id}, minutes={minutes}",
        )
    await message.reply(f"User {target_user_id} removed. They can rejoin after {minutes} minutes.")


@router.message(Command("mute"))
async def mute_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    if message.from_user is None:
        return

    target_user_id = parse_target_user_id(message, command)
    if target_user_id is None:
        await message.reply("Usage: reply + /mute [minutes], or /mute user_id [minutes]")
        return

    minutes = parse_minutes(command, 30)
    until_date = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    await message.bot.restrict_chat_member(
        chat_id=message.chat.id,
        user_id=target_user_id,
        permissions=ChatPermissions(can_send_messages=False),
        until_date=until_date,
    )
    async with SessionLocal() as db:
        await add_log(
            db,
            message.chat.id,
            message.from_user.id,
            message.from_user.username or "",
            "manual_mute",
            f"target={target_user_id}, minutes={minutes}",
        )
    await message.reply(f"User {target_user_id} muted for {minutes} minutes.")


@router.message(Command("unmute"))
async def unmute_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    if message.from_user is None:
        return

    target_user_id = parse_target_user_id(message, command)
    if target_user_id is None:
        await message.reply("Usage: reply + /unmute, or /unmute user_id")
        return

    await message.bot.restrict_chat_member(
        chat_id=message.chat.id,
        user_id=target_user_id,
        permissions=ChatPermissions(can_send_messages=True),
    )
    async with SessionLocal() as db:
        await add_log(
            db,
            message.chat.id,
            message.from_user.id,
            message.from_user.username or "",
            "manual_unmute",
            f"target={target_user_id}",
        )
    await message.reply(f"User {target_user_id} unmuted.")
