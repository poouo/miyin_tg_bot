import asyncio
from datetime import datetime, timedelta, timezone
from html import escape
import json
import random

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import ChatPermissions, Message

from apps.api.app.core.db import SessionLocal
from apps.api.app.services.community_feature_service import (
    DISABLEABLE_COMMANDS,
    LOCK_TYPES,
    add_warning,
    add_global_ban,
    add_rss_subscription,
    clear_rules,
    delete_note,
    disable_command,
    enable_command,
    get_lock_config,
    get_log_channel,
    get_note,
    get_report_config,
    get_rules,
    get_user_profile,
    get_welcome_config,
    get_warning_setting,
    is_command_disabled,
    list_notes,
    list_disabled_commands,
    list_global_bans,
    list_rss_subscriptions,
    list_warnings,
    remove_global_ban,
    remove_rss_subscription,
    reset_warnings,
    set_afk,
    save_note,
    set_lock,
    set_log_channel,
    set_reports_enabled,
    set_rules,
    unset_log_channel,
    update_welcome_config,
    update_user_profile,
    update_warning_setting,
)
from apps.api.app.services.group_service import ensure_group, get_group, list_groups
from apps.api.app.services.log_service import add_log
from apps.api.app.services.moderation.auto_recover import add_ban_sanction, mark_ban_recovered
from apps.api.app.services.moderation.join_verification import challenge_failure_reason, get_challenge, verify_challenge
from apps.api.app.services.runtime_config_service import get_runtime_config
from apps.bot.bot_app.ai_formatting import reply_ai_text
from apps.bot.bot_app.moderation_actions import DEFAULT_KICK_MINUTES, ModerationActionConfig, apply_moderation_action
from apps.bot.bot_app.state import deepseek_client
from apps.bot.bot_app.verification_notices import (
    delete_message_later,
    send_temporary_notice,
    send_verify_fail_notice,
    send_verify_pass_notice,
)

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


async def delete_verification_message(bot, chat_id: int, challenge) -> None:
    message_id = int(getattr(challenge, "message_id", 0) or 0)
    if message_id <= 0:
        return
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception:
        return


USER_HELP_TEXT = "\n".join(
    [
        "<b>可用指令</b>",
        "<code>/ping</code> - 检查机器人状态",
        "<code>/ask 问题</code> - 与 AI 聊天",
        "<code>/rules</code> - 查看群规则",
        "<code>/notes</code> - 查看群笔记",
        "<code>/get 名称</code> - 读取群笔记",
        "<code>/warns</code> - 查看自己的警告",
        "<code>/report</code> - 回复消息举报给管理员",
        "<code>/id</code> - 查看用户/群组 ID",
        "<code>/afk 原因</code> - 设置离开状态",
        "<code>/runs</code> / <code>/slap</code> - 趣味互动",
        "<code>/stickerid</code> - 回复贴纸查看 ID",
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
        "<code>/warn 用户ID 原因</code> - 警告用户",
        "<code>/resetwarn 用户ID</code> - 清空警告",
        "<code>/warnlimit 数量</code> - 设置警告阈值",
        "<code>/strongwarn mute|kick|ban 分钟</code> - 设置警告满后的处理",
        "<code>/setrules 文本</code> - 设置群规则",
        "<code>/clearrules</code> - 清空群规则",
        "<code>/save 名称 内容</code> - 保存群笔记",
        "<code>/clear 名称</code> - 删除群笔记",
        "<code>/reports on|off</code> - 开关举报",
        "<code>/lock 类型</code> / <code>/unlock 类型</code> - 锁定消息类型",
        "<code>/locks</code> - 查看锁状态",
        "<code>/adminlist</code> - 查看管理员列表",
        "<code>/pin</code> / <code>/unpin</code> - 置顶/取消置顶消息",
        "<code>/welcome on|off</code> - 开关欢迎",
        "<code>/setwelcome 文本</code> - 设置欢迎语",
        "<code>/goodbye on|off</code> - 开关退群提示",
        "<code>/setgoodbye 文本</code> - 设置退群提示",
        "<code>/setlog 群ID</code> / <code>/unsetlog</code> - 设置日志频道",
        "<code>/gban 用户ID 原因</code> / <code>/ungban 用户ID</code> - 全局封禁",
        "<code>/disable 指令</code> / <code>/enable 指令</code> - 禁用普通指令",
        "<code>/disabled</code> - 查看禁用指令",
        "<code>/purge</code> / <code>/del</code> - 清理消息",
        "<code>/addrss URL</code> / <code>/removerss URL</code> / <code>/listrss</code> - RSS 配置",
        "<code>/setbio 文本</code> / <code>/bio</code> - 用户简介",
        "<code>/setme 文本</code> / <code>/me</code> - 个人说明",
        "<code>/export</code> - 导出群配置",
        "<code>/import JSON</code> - 导入群配置",
        "<code>/broadcast 文本</code> - 后台管理员广播",
        "<i>群内可回复用户消息后使用；私聊需写成 /unban 群组ID 用户ID。</i>",
    ]
)
ADMIN_ONLY_TEXT = "<b>权限不足</b>\n此指令仅群管理员可用。"
PRIVATE_ADMIN_ONLY_TEXT = "<b>权限不足</b>\n私聊管理指令仅后台配置的管理员 ID 可用。"


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


async def is_private_admin(message: Message) -> bool:
    if message.from_user is None or message.chat.type != "private":
        return False
    async with SessionLocal() as db:
        runtime = await get_runtime_config(db)
    return message.from_user.id in runtime.telegram_admin_id_list


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


def split_first_arg(command: CommandObject) -> tuple[str, str]:
    args = (command.args or "").strip()
    if not args:
        return "", ""
    parts = args.split(maxsplit=1)
    return parts[0], parts[1] if len(parts) > 1 else ""


def target_label(message: Message, user_id: int) -> str:
    if message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == user_id:
        user = message.reply_to_message.from_user
        return f'<a href="tg://user?id={user.id}">{escape(user.full_name)}</a>'
    return f"<code>{user_id}</code>"


async def reply_note(message: Message, text: str, parse_mode: str) -> None:
    mode = (parse_mode or "plain").lower()
    kwargs: dict = {}
    if mode == "markdownv2":
        kwargs["parse_mode"] = "MarkdownV2"
    elif mode == "html":
        kwargs["parse_mode"] = "HTML"
    try:
        await message.reply(text[:3800], **kwargs)
    except Exception:
        await message.reply(text[:3800])


def current_command_name(message: Message) -> str:
    text = message.text or ""
    if not text.startswith("/"):
        return ""
    return text.split(maxsplit=1)[0].lstrip("/").split("@")[0].lower()


async def blocked_by_disable(message: Message) -> bool:
    if message.chat.type not in {"group", "supergroup"}:
        return False
    command = current_command_name(message)
    if command not in DISABLEABLE_COMMANDS:
        return False
    if await is_group_manager(message):
        return False
    async with SessionLocal() as db:
        disabled = await is_command_disabled(db, message.chat.id, command)
    if not disabled:
        return False
    try:
        await message.delete()
    except Exception:
        pass
    return True

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
    if await is_group_manager(message) or await is_private_admin(message):
        await message.reply(ADMIN_HELP_TEXT, parse_mode="HTML")
        return
    await message.reply(USER_HELP_TEXT, parse_mode="HTML")


async def require_group_manager(message: Message) -> bool:
    if await is_group_manager(message):
        return True
    await message.reply(ADMIN_ONLY_TEXT, parse_mode="HTML")
    return False


async def require_moderation_admin(message: Message) -> bool:
    if message.chat.type in {"group", "supergroup"}:
        return await require_group_manager(message)
    if await is_private_admin(message):
        return True
    await message.reply(PRIVATE_ADMIN_ONLY_TEXT, parse_mode="HTML")
    return False


def parse_private_admin_args(command: CommandObject) -> tuple[int, int, int | None] | None:
    args = (command.args or "").strip().split()
    if len(args) < 2:
        return None
    try:
        chat_id = int(args[0])
        user_id = int(args[1])
        minutes = int(args[2]) if len(args) > 2 else None
        return chat_id, user_id, minutes
    except ValueError:
        return None


def resolve_moderation_target(message: Message, command: CommandObject) -> tuple[int, int, int | None] | None:
    if message.chat.type == "private":
        return parse_private_admin_args(command)
    target_user_id = parse_target_user_id(message, command)
    if target_user_id is None:
        return None
    return message.chat.id, target_user_id, None


@router.message(Command("ask"))
async def ask_handler(message: Message, command: CommandObject) -> None:
    if await blocked_by_disable(message):
        return
    question = (command.args or "").strip()
    if not question:
        await message.reply("Usage: /ask your question")
        return

    chat = message.chat
    group = None
    async with SessionLocal() as db:
        if chat.type in {"group", "supergroup"}:
            await ensure_group(db, chat.id, chat.title or "")
            group = await get_group(db, chat.id)
            if group and not group.deepseek_enabled:
                await message.reply("AI is disabled in this group.")
                return
        answer = await deepseek_client.ask(question, db=db)
    sent = await reply_ai_text(message, answer)
    delete_after_seconds = int(getattr(group, "ai_reply_delete_after_seconds", 0) or 0)
    if sent is not None and delete_after_seconds > 0:
        asyncio.create_task(delete_message_later(message.bot, chat.id, sent.message_id, delete_after_seconds))


@router.message(Command("id"))
async def id_handler(message: Message) -> None:
    if await blocked_by_disable(message):
        return
    await register_group_if_needed(message)
    lines = [f"Chat ID: <code>{message.chat.id}</code>"]
    if message.from_user is not None:
        lines.append(f"Your ID: <code>{message.from_user.id}</code>")
    if message.reply_to_message and message.reply_to_message.from_user:
        lines.append(f"Replied user ID: <code>{message.reply_to_message.from_user.id}</code>")
    await message.reply("\n".join(lines), parse_mode="HTML")


@router.message(Command("adminlist", "staff"))
async def adminlist_handler(message: Message) -> None:
    if await blocked_by_disable(message):
        return
    await register_group_if_needed(message)
    if message.chat.type not in {"group", "supergroup"}:
        await message.reply("请在群组内使用。")
        return
    admins = await message.bot.get_chat_administrators(message.chat.id)
    lines = ["<b>管理员列表</b>"]
    for item in admins:
        user = item.user
        if user.is_bot:
            continue
        title = f" - {escape(item.custom_title)}" if getattr(item, "custom_title", None) else ""
        lines.append(f'<a href="tg://user?id={user.id}">{escape(user.full_name)}</a>{title}')
    await message.reply("\n".join(lines), parse_mode="HTML")


@router.message(Command("pin"))
async def pin_handler(message: Message) -> None:
    if not await require_group_manager(message):
        return
    if message.reply_to_message is None:
        await message.reply("请回复要置顶的消息后使用 /pin。")
        return
    await message.bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id, disable_notification=True)
    await message.reply("已置顶。")


@router.message(Command("unpin"))
async def unpin_handler(message: Message) -> None:
    if not await require_group_manager(message):
        return
    if message.reply_to_message is not None:
        await message.bot.unpin_chat_message(message.chat.id, message.reply_to_message.message_id)
    else:
        await message.bot.unpin_chat_message(message.chat.id)
    await message.reply("已取消置顶。")


@router.message(Command("del"))
async def delete_replied_handler(message: Message) -> None:
    if not await require_group_manager(message):
        return
    if message.reply_to_message is None:
        await message.reply("请回复要删除的消息后使用 /del。")
        return
    try:
        await message.reply_to_message.delete()
        await message.delete()
    except Exception:
        await message.reply("删除失败，请确认机器人有删除消息权限。")


@router.message(Command("purge"))
async def purge_handler(message: Message) -> None:
    if not await require_group_manager(message):
        return
    if message.reply_to_message is None:
        await message.reply("请回复起始消息后使用 /purge。")
        return
    start_id = message.reply_to_message.message_id
    end_id = message.message_id
    deleted = 0
    for message_id in range(start_id, end_id + 1):
        try:
            await message.bot.delete_message(message.chat.id, message_id)
            deleted += 1
        except Exception:
            continue
    await send_temporary_notice(message.bot, message.chat.id, f"已清理 {deleted} 条消息。", seconds=10)


@router.message(Command("afk"))
async def afk_handler(message: Message, command: CommandObject) -> None:
    if message.from_user is None:
        return
    reason = (command.args or "").strip()[:1000]
    async with SessionLocal() as db:
        await set_afk(db, message.from_user.id, reason)
    await message.reply(f"已设置 AFK。{escape(reason)}" if reason else "已设置 AFK。", parse_mode="HTML")


@router.message(Command("runs"))
async def runs_handler(message: Message) -> None:
    if await blocked_by_disable(message):
        return
    await message.reply(random.choice(["跑得飞快。", "我先撤一步。", "风一样路过。", "还在，还没跑。"]))


@router.message(Command("slap"))
async def slap_handler(message: Message, command: CommandObject) -> None:
    if await blocked_by_disable(message):
        return
    target = "自己"
    if message.reply_to_message and message.reply_to_message.from_user:
        target = escape(message.reply_to_message.from_user.full_name)
    else:
        first, _ = split_first_arg(command)
        if first:
            target = escape(first)
    await message.reply(f"轻轻拍了一下 <b>{target}</b>。", parse_mode="HTML")


@router.message(Command("stickerid"))
async def stickerid_handler(message: Message) -> None:
    if message.reply_to_message is None or message.reply_to_message.sticker is None:
        await message.reply("请回复一个贴纸后使用 /stickerid。")
        return
    sticker = message.reply_to_message.sticker
    await message.reply(f"Sticker ID:\n<code>{sticker.file_id}</code>", parse_mode="HTML")


@router.message(Command("markdownhelp"))
async def markdownhelp_handler(message: Message) -> None:
    await message.reply(
        "\n".join(
            [
                "<b>格式化提示</b>",
                "HTML: <code>&lt;b&gt;粗体&lt;/b&gt;</code>",
                "HTML: <code>&lt;i&gt;斜体&lt;/i&gt;</code>",
                "HTML: <code>&lt;code&gt;代码&lt;/code&gt;</code>",
                "自动回复和笔记支持 plain / HTML / MarkdownV2。",
            ]
        ),
        parse_mode="HTML",
    )


@router.message(Command("setbio"))
async def setbio_handler(message: Message, command: CommandObject) -> None:
    if message.from_user is None:
        return
    text = (command.args or "").strip()
    if not text:
        await message.reply("Usage: /setbio 简介")
        return
    async with SessionLocal() as db:
        await update_user_profile(db, message.from_user.id, bio=text[:1000])
    await message.reply("简介已保存。")


@router.message(Command("bio"))
async def bio_handler(message: Message, command: CommandObject) -> None:
    target_user_id = parse_target_user_id(message, command)
    if target_user_id is None and message.from_user is not None:
        target_user_id = message.from_user.id
    if target_user_id is None:
        return
    async with SessionLocal() as db:
        profile = await get_user_profile(db, target_user_id)
    await message.reply(profile.bio or "这个用户还没有设置简介。")


@router.message(Command("setme"))
async def setme_handler(message: Message, command: CommandObject) -> None:
    if message.from_user is None:
        return
    text = (command.args or "").strip()
    if not text:
        await message.reply("Usage: /setme 个人说明")
        return
    async with SessionLocal() as db:
        await update_user_profile(db, message.from_user.id, about=text[:1000])
    await message.reply("个人说明已保存。")


@router.message(Command("me"))
async def me_handler(message: Message, command: CommandObject) -> None:
    target_user_id = parse_target_user_id(message, command)
    if target_user_id is None and message.from_user is not None:
        target_user_id = message.from_user.id
    if target_user_id is None:
        return
    async with SessionLocal() as db:
        profile = await get_user_profile(db, target_user_id)
    await message.reply(profile.about or "这个用户还没有设置个人说明。")


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
            challenge = await get_challenge(db, chat_id, user_id)
            if challenge is not None:
                await delete_verification_message(message.bot, chat_id, challenge)
                challenge.message_id = 0
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
            fail_reason = challenge_failure_reason(challenge, answer)
            if challenge is not None and not challenge.passed:
                await delete_verification_message(message.bot, chat_id, challenge)
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
                    fail_reason,
                )
                challenge.passed = True
                challenge.message_id = 0
                await db.commit()
            else:
                await send_temporary_notice(message.bot, chat_id, f"验证失败：{fail_reason}")
            await add_log(db, chat_id, user_id, message.from_user.username or "", "join_verify_failed", fail_reason)


@router.message(Command("rules"))
async def rules_handler(message: Message) -> None:
    if await blocked_by_disable(message):
        return
    await register_group_if_needed(message)
    if message.chat.type not in {"group", "supergroup"}:
        await message.reply("请在群组内使用 /rules。")
        return
    async with SessionLocal() as db:
        entity = await get_rules(db, message.chat.id)
    if entity is None or not entity.rules_text.strip():
        await message.reply("本群暂未设置规则。")
        return
    await message.reply(f"<b>群规则</b>\n\n{escape(entity.rules_text)}", parse_mode="HTML")


@router.message(Command("setrules"))
async def setrules_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    text = (command.args or "").strip()
    if not text:
        await message.reply("Usage: /setrules 群规则文本")
        return
    async with SessionLocal() as db:
        await ensure_group(db, message.chat.id, message.chat.title or "")
        await set_rules(db, message.chat.id, text[:4000])
        await add_log(db, message.chat.id, message.from_user.id if message.from_user else 0, "", "rules_set", "")
    await message.reply("群规则已更新。")


@router.message(Command("clearrules"))
async def clearrules_handler(message: Message) -> None:
    if not await require_group_manager(message):
        return
    async with SessionLocal() as db:
        await clear_rules(db, message.chat.id)
        await add_log(db, message.chat.id, message.from_user.id if message.from_user else 0, "", "rules_cleared", "")
    await message.reply("群规则已清空。")


@router.message(Command("welcome"))
async def welcome_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    arg = (command.args or "").strip().lower()
    async with SessionLocal() as db:
        config = await get_welcome_config(db, message.chat.id)
        if arg in {"on", "yes", "true"}:
            config = await update_welcome_config(db, message.chat.id, welcome_enabled=True)
        elif arg in {"off", "no", "false"}:
            config = await update_welcome_config(db, message.chat.id, welcome_enabled=False)
    await message.reply(f"欢迎消息：{'开启' if config.welcome_enabled else '关闭'}。")


@router.message(Command("setwelcome"))
async def setwelcome_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    text = (command.args or "").strip()
    if not text:
        await message.reply("Usage: /setwelcome 欢迎 {mention} 加入 {chat_title}")
        return
    async with SessionLocal() as db:
        await update_welcome_config(db, message.chat.id, welcome_text=text[:4000], welcome_enabled=True)
    await message.reply("欢迎语已更新。")


@router.message(Command("resetwelcome"))
async def resetwelcome_handler(message: Message) -> None:
    if not await require_group_manager(message):
        return
    async with SessionLocal() as db:
        await update_welcome_config(
            db,
            message.chat.id,
            welcome_text="欢迎 {fullname} 加入 {chat_title}。",
            welcome_enabled=True,
        )
    await message.reply("欢迎语已重置。")


@router.message(Command("cleanwelcome"))
async def cleanwelcome_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    arg = (command.args or "").strip().lower()
    enabled = arg not in {"off", "no", "false", "0"}
    async with SessionLocal() as db:
        await update_welcome_config(db, message.chat.id, clean_welcome=enabled)
    await message.reply(f"旧欢迎消息自动清理：{'开启' if enabled else '关闭'}。")


@router.message(Command("goodbye"))
async def goodbye_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    arg = (command.args or "").strip().lower()
    async with SessionLocal() as db:
        config = await get_welcome_config(db, message.chat.id)
        if arg in {"on", "yes", "true"}:
            config = await update_welcome_config(db, message.chat.id, goodbye_enabled=True)
        elif arg in {"off", "no", "false"}:
            config = await update_welcome_config(db, message.chat.id, goodbye_enabled=False)
    await message.reply(f"退群提示：{'开启' if config.goodbye_enabled else '关闭'}。")


@router.message(Command("setgoodbye"))
async def setgoodbye_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    text = (command.args or "").strip()
    if not text:
        await message.reply("Usage: /setgoodbye {fullname} 离开了 {chat_title}")
        return
    async with SessionLocal() as db:
        await update_welcome_config(db, message.chat.id, goodbye_text=text[:4000], goodbye_enabled=True)
    await message.reply("退群提示已更新。")


@router.message(Command("resetgoodbye"))
async def resetgoodbye_handler(message: Message) -> None:
    if not await require_group_manager(message):
        return
    async with SessionLocal() as db:
        await update_welcome_config(
            db,
            message.chat.id,
            goodbye_text="{fullname} 离开了 {chat_title}。",
            goodbye_enabled=False,
        )
    await message.reply("退群提示已重置。")


@router.message(Command("save"))
async def save_note_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    name, text = split_first_arg(command)
    if not name or not text:
        await message.reply("Usage: /save 名称 内容")
        return
    async with SessionLocal() as db:
        await save_note(db, message.chat.id, name, text[:4000])
        await add_log(db, message.chat.id, message.from_user.id if message.from_user else 0, "", "note_saved", name)
    await message.reply(f"笔记 <code>{escape(name.lstrip('#'))}</code> 已保存。", parse_mode="HTML")


@router.message(Command("get"))
async def get_note_handler(message: Message, command: CommandObject) -> None:
    if await blocked_by_disable(message):
        return
    await register_group_if_needed(message)
    name = (command.args or "").strip()
    if not name:
        await message.reply("Usage: /get 名称")
        return
    async with SessionLocal() as db:
        note = await get_note(db, message.chat.id, name)
    if note is None:
        await message.reply("没有找到这个笔记。")
        return
    await reply_note(message, note.text, note.parse_mode)


@router.message(Command("notes", "saved"))
async def list_notes_handler(message: Message) -> None:
    if await blocked_by_disable(message):
        return
    await register_group_if_needed(message)
    async with SessionLocal() as db:
        notes = await list_notes(db, message.chat.id)
    if not notes:
        await message.reply("本群暂未保存笔记。")
        return
    body = "\n".join(f"- <code>{escape(item.name)}</code>" for item in notes[:80])
    await message.reply(f"<b>群笔记</b>\n{body}", parse_mode="HTML")


@router.message(Command("clear"))
async def clear_note_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    name = (command.args or "").strip()
    if not name:
        await message.reply("Usage: /clear 名称")
        return
    async with SessionLocal() as db:
        deleted = await delete_note(db, message.chat.id, name)
        await add_log(db, message.chat.id, message.from_user.id if message.from_user else 0, "", "note_deleted", name)
    await message.reply("笔记已删除。" if deleted else "没有找到这个笔记。")


@router.message(Command("warn"))
async def warn_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    if message.from_user is None:
        return
    target_user_id = parse_target_user_id(message, command)
    if target_user_id is None:
        await message.reply("Usage: reply + /warn [原因], or /warn 用户ID [原因]")
        return
    reason = (command.args or "").strip()
    if reason and reason.split()[0].lstrip("-").isdigit():
        reason = " ".join(reason.split()[1:])
    async with SessionLocal() as db:
        _, total, setting = await add_warning(db, message.chat.id, target_user_id, message.from_user.id, reason[:1000])
        await add_log(db, message.chat.id, target_user_id, message.from_user.username or "", "warned", reason)
        if total >= setting.warn_limit:
            await reset_warnings(db, message.chat.id, target_user_id)
            await apply_moderation_action(
                message.bot,
                db,
                message.chat.id,
                target_user_id,
                "",
                "warn_limit",
                ModerationActionConfig(
                    action=setting.warn_action,
                    kick_minutes=DEFAULT_KICK_MINUTES,
                    mute_minutes=setting.mute_minutes,
                    ban_minutes=setting.ban_minutes,
                ),
            )
            await message.reply(
                f"{target_label(message, target_user_id)} 已达到警告阈值，已执行 {escape(setting.warn_action)}。",
                parse_mode="HTML",
            )
            return
    await message.reply(
        f"{target_label(message, target_user_id)} 已被警告：<b>{total}</b>/<b>{setting.warn_limit}</b>",
        parse_mode="HTML",
    )


@router.message(Command("warns"))
async def warns_handler(message: Message, command: CommandObject) -> None:
    if await blocked_by_disable(message):
        return
    await register_group_if_needed(message)
    target_user_id = parse_target_user_id(message, command)
    if target_user_id is None and message.from_user is not None:
        target_user_id = message.from_user.id
    if target_user_id is None:
        return
    async with SessionLocal() as db:
        warnings = await list_warnings(db, message.chat.id, target_user_id)
        setting = await get_warning_setting(db, message.chat.id)
    if not warnings:
        await message.reply("没有警告记录。")
        return
    lines = [f"<b>警告记录</b> {len(warnings)}/{setting.warn_limit}"]
    for index, item in enumerate(warnings[-10:], start=1):
        lines.append(f"{index}. {escape(item.reason or '未填写原因')}")
    await message.reply("\n".join(lines), parse_mode="HTML")


@router.message(Command("resetwarn", "resetwarns"))
async def resetwarn_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    target_user_id = parse_target_user_id(message, command)
    if target_user_id is None:
        await message.reply("Usage: reply + /resetwarn, or /resetwarn 用户ID")
        return
    async with SessionLocal() as db:
        count = await reset_warnings(db, message.chat.id, target_user_id)
        await add_log(db, message.chat.id, target_user_id, "", "warns_reset", str(count))
    await message.reply(f"已清空 {count} 条警告。")


@router.message(Command("warnlimit"))
async def warnlimit_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    try:
        limit = int((command.args or "").strip())
    except ValueError:
        await message.reply("Usage: /warnlimit 3")
        return
    async with SessionLocal() as db:
        setting = await update_warning_setting(db, message.chat.id, warn_limit=limit)
    await message.reply(f"警告阈值已设置为 {setting.warn_limit}。")


@router.message(Command("strongwarn"))
async def strongwarn_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    action, rest = split_first_arg(command)
    if action not in {"mute", "kick", "ban"}:
        await message.reply("Usage: /strongwarn mute|kick|ban [分钟]")
        return
    minutes = None
    if rest:
        try:
            minutes = int(rest.split()[0])
        except ValueError:
            minutes = None
    async with SessionLocal() as db:
        setting = await update_warning_setting(db, message.chat.id, warn_action=action, minutes=minutes)
    await message.reply(
        f"警告满后的处理已设置为 {setting.warn_action}。mute={setting.mute_minutes} 分钟，ban={setting.ban_minutes} 分钟。"
    )


@router.message(Command("report"))
async def report_handler(message: Message) -> None:
    if await blocked_by_disable(message):
        return
    await register_group_if_needed(message)
    if message.chat.type not in {"group", "supergroup"}:
        return
    if message.reply_to_message is None or message.from_user is None:
        await message.reply("请回复要举报的消息后使用 /report。")
        return
    async with SessionLocal() as db:
        config = await get_report_config(db, message.chat.id)
    if not config.enabled:
        await message.reply("本群未开启举报。")
        return
    admins = await message.bot.get_chat_administrators(message.chat.id)
    mentions = []
    for admin in admins:
        user = admin.user
        if user.is_bot:
            continue
        mentions.append(f'<a href="tg://user?id={user.id}">{escape(user.full_name)}</a>')
    if not mentions:
        await message.reply("没有可通知的管理员。")
        return
    await message.reply(
        f"<b>用户举报</b>\n举报人：{escape(message.from_user.full_name)}\n管理员：{' '.join(mentions[:8])}",
        parse_mode="HTML",
    )


@router.message(Command("reports"))
async def reports_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    arg = (command.args or "").strip().lower()
    if arg not in {"on", "off"}:
        async with SessionLocal() as db:
            config = await get_report_config(db, message.chat.id)
        await message.reply(f"举报当前状态：{'开启' if config.enabled else '关闭'}。Usage: /reports on|off")
        return
    async with SessionLocal() as db:
        config = await set_reports_enabled(db, message.chat.id, arg == "on")
    await message.reply(f"举报已{'开启' if config.enabled else '关闭'}。")


@router.message(Command("logchannel"))
async def logchannel_handler(message: Message) -> None:
    if not await require_group_manager(message):
        return
    async with SessionLocal() as db:
        config = await get_log_channel(db, message.chat.id)
    if config.enabled and config.log_chat_id:
        await message.reply(f"日志频道：<code>{config.log_chat_id}</code>", parse_mode="HTML")
    else:
        await message.reply("日志频道未设置。")


@router.message(Command("setlog"))
async def setlog_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    raw = (command.args or "").strip()
    try:
        log_chat_id = int(raw)
    except ValueError:
        await message.reply("Usage: /setlog 日志群或频道ID")
        return
    async with SessionLocal() as db:
        await set_log_channel(db, message.chat.id, log_chat_id, True)
    await message.reply(f"日志频道已设置为 <code>{log_chat_id}</code>。", parse_mode="HTML")


@router.message(Command("unsetlog"))
async def unsetlog_handler(message: Message) -> None:
    if not await require_group_manager(message):
        return
    async with SessionLocal() as db:
        await unset_log_channel(db, message.chat.id)
    await message.reply("日志频道已关闭。")


@router.message(Command("gban"))
async def gban_handler(message: Message, command: CommandObject) -> None:
    if not await require_moderation_admin(message):
        return
    if message.from_user is None:
        return
    resolved = resolve_moderation_target(message, command)
    if resolved is None:
        await message.reply("Usage: reply + /gban [原因], /gban 用户ID [原因], or private /gban 群组ID 用户ID [原因]")
        return
    chat_id, target_user_id, _ = resolved
    reason = (command.args or "").strip()
    parts = reason.split()
    if message.chat.type == "private" and len(parts) > 2:
        reason = " ".join(parts[2:])
    elif parts and parts[0].lstrip("-").isdigit():
        reason = " ".join(parts[1:])
    async with SessionLocal() as db:
        await add_global_ban(db, target_user_id, message.from_user.id, reason[:1000])
        await add_log(db, chat_id, target_user_id, message.from_user.username or "", "global_ban", reason)
    try:
        await message.bot.ban_chat_member(chat_id, target_user_id)
    except Exception:
        pass
    await message.reply(f"用户 <code>{target_user_id}</code> 已加入全局封禁。", parse_mode="HTML")


@router.message(Command("ungban"))
async def ungban_handler(message: Message, command: CommandObject) -> None:
    if not await require_moderation_admin(message):
        return
    target_user_id = parse_target_user_id(message, command)
    if message.chat.type == "private":
        parsed = parse_private_admin_args(command)
        target_user_id = parsed[1] if parsed else None
    if target_user_id is None:
        await message.reply("Usage: /ungban 用户ID")
        return
    async with SessionLocal() as db:
        removed = await remove_global_ban(db, target_user_id)
    await message.reply("全局封禁已解除。" if removed else "该用户不在全局封禁列表。")


@router.message(Command("gbanlist"))
async def gbanlist_handler(message: Message) -> None:
    if not await require_moderation_admin(message):
        return
    async with SessionLocal() as db:
        items = await list_global_bans(db)
    if not items:
        await message.reply("全局封禁列表为空。")
        return
    lines = ["<b>全局封禁</b>"]
    for item in items[:80]:
        lines.append(f"<code>{item.user_id}</code> - {escape(item.reason or '无原因')}")
    await message.reply("\n".join(lines), parse_mode="HTML")


@router.message(Command("disable"))
async def disable_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    name = (command.args or "").strip()
    if not name:
        await message.reply(f"可禁用：{', '.join(sorted(DISABLEABLE_COMMANDS))}")
        return
    async with SessionLocal() as db:
        entity = await disable_command(db, message.chat.id, name)
    await message.reply("指令已禁用。" if entity else "该指令不支持禁用。")


@router.message(Command("enable"))
async def enable_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    name = (command.args or "").strip()
    if not name:
        await message.reply("Usage: /enable 指令")
        return
    async with SessionLocal() as db:
        removed = await enable_command(db, message.chat.id, name)
    await message.reply("指令已启用。" if removed else "该指令未被禁用。")


@router.message(Command("disabled", "cmds"))
async def disabled_handler(message: Message) -> None:
    if not await require_group_manager(message):
        return
    async with SessionLocal() as db:
        items = await list_disabled_commands(db, message.chat.id)
    await message.reply("已禁用：" + (", ".join(items) if items else "无"))


@router.message(Command("addrss"))
async def addrss_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    url = (command.args or "").strip()
    if not url:
        await message.reply("Usage: /addrss https://example.com/feed.xml")
        return
    async with SessionLocal() as db:
        await add_rss_subscription(db, message.chat.id, url)
    await message.reply("RSS 订阅已保存。")


@router.message(Command("removerss"))
async def removerss_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    url = (command.args or "").strip()
    if not url:
        await message.reply("Usage: /removerss URL")
        return
    async with SessionLocal() as db:
        removed = await remove_rss_subscription(db, message.chat.id, url)
    await message.reply("RSS 订阅已删除。" if removed else "没有找到这个 RSS 订阅。")


@router.message(Command("listrss", "rss"))
async def listrss_handler(message: Message) -> None:
    await register_group_if_needed(message)
    async with SessionLocal() as db:
        items = await list_rss_subscriptions(db, message.chat.id)
    if not items:
        await message.reply("本群暂无 RSS 订阅。")
        return
    lines = ["<b>RSS 订阅</b>"]
    for item in items[:50]:
        lines.append(f"- {escape(item.title or item.url)}")
    await message.reply("\n".join(lines), parse_mode="HTML")


@router.message(Command("export"))
async def export_handler(message: Message) -> None:
    if not await require_group_manager(message):
        return
    async with SessionLocal() as db:
        rules = await get_rules(db, message.chat.id)
        notes = await list_notes(db, message.chat.id)
        locks = await get_lock_config(db, message.chat.id)
        welcome = await get_welcome_config(db, message.chat.id)
        reports = await get_report_config(db, message.chat.id)
        disabled = await list_disabled_commands(db, message.chat.id)
        rss_items = await list_rss_subscriptions(db, message.chat.id)
    payload = {
        "rules": rules.rules_text if rules else "",
        "notes": [{"name": item.name, "text": item.text, "parse_mode": item.parse_mode} for item in notes],
        "locks": {item: bool(getattr(locks, item)) for item in sorted(LOCK_TYPES)},
        "welcome": {
            "welcome_enabled": welcome.welcome_enabled,
            "goodbye_enabled": welcome.goodbye_enabled,
            "clean_welcome": welcome.clean_welcome,
            "welcome_text": welcome.welcome_text,
            "goodbye_text": welcome.goodbye_text,
        },
        "reports_enabled": reports.enabled,
        "disabled_commands": disabled,
        "rss": [{"url": item.url, "title": item.title} for item in rss_items],
    }
    await message.reply(f"<pre>{escape(json.dumps(payload, ensure_ascii=False, indent=2))}</pre>", parse_mode="HTML")


@router.message(Command("import"))
async def import_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    raw = (command.args or "").strip()
    if not raw and message.reply_to_message and message.reply_to_message.text:
        raw = message.reply_to_message.text.strip()
    if not raw:
        await message.reply("Usage: /import JSON，或回复导出的 JSON 后发送 /import")
        return
    raw = raw.removeprefix("<pre>").removesuffix("</pre>").strip()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        await message.reply("导入失败：JSON 格式无效。")
        return
    async with SessionLocal() as db:
        if isinstance(payload.get("rules"), str):
            await set_rules(db, message.chat.id, payload["rules"][:4000])
        for note in payload.get("notes", []) if isinstance(payload.get("notes"), list) else []:
            if isinstance(note, dict) and note.get("name") and note.get("text"):
                await save_note(db, message.chat.id, str(note["name"]), str(note["text"])[:4000], str(note.get("parse_mode") or "plain"))
        locks = payload.get("locks")
        if isinstance(locks, dict):
            for key, value in locks.items():
                await set_lock(db, message.chat.id, str(key), bool(value))
        welcome = payload.get("welcome")
        if isinstance(welcome, dict):
            await update_welcome_config(
                db,
                message.chat.id,
                welcome_enabled=welcome.get("welcome_enabled"),
                goodbye_enabled=welcome.get("goodbye_enabled"),
                clean_welcome=welcome.get("clean_welcome"),
                welcome_text=welcome.get("welcome_text"),
                goodbye_text=welcome.get("goodbye_text"),
            )
        if "reports_enabled" in payload:
            await set_reports_enabled(db, message.chat.id, bool(payload["reports_enabled"]))
        for command_name in payload.get("disabled_commands", []) if isinstance(payload.get("disabled_commands"), list) else []:
            await disable_command(db, message.chat.id, str(command_name))
        for item in payload.get("rss", []) if isinstance(payload.get("rss"), list) else []:
            if isinstance(item, dict) and item.get("url"):
                await add_rss_subscription(db, message.chat.id, str(item["url"]), str(item.get("title") or ""))
    await message.reply("配置已导入。")


@router.message(Command("broadcast"))
async def broadcast_handler(message: Message, command: CommandObject) -> None:
    if not await is_private_admin(message):
        await message.reply(PRIVATE_ADMIN_ONLY_TEXT, parse_mode="HTML")
        return
    text = (command.args or "").strip()
    if not text:
        await message.reply("Usage: /broadcast 文本")
        return
    sent = 0
    async with SessionLocal() as db:
        groups = await list_groups(db)
    for group in groups:
        try:
            await message.bot.send_message(group.chat_id, text[:3800])
            sent += 1
        except Exception:
            continue
    await message.reply(f"广播完成，成功发送 {sent} 个群。")


@router.message(Command("lock", "unlock"))
async def lock_handler(message: Message, command: CommandObject) -> None:
    if not await require_group_manager(message):
        return
    lock_type = (command.args or "").strip().lower()
    if lock_type not in LOCK_TYPES:
        await message.reply(f"Usage: /lock {'|'.join(sorted(LOCK_TYPES))}")
        return
    enabled = (message.text or "").split()[0].lstrip("/").split("@")[0] == "lock"
    async with SessionLocal() as db:
        await set_lock(db, message.chat.id, lock_type, enabled)
    await message.reply(f"{lock_type} 已{'锁定' if enabled else '解锁'}。")


@router.message(Command("locks"))
async def locks_handler(message: Message) -> None:
    await register_group_if_needed(message)
    async with SessionLocal() as db:
        config = await get_lock_config(db, message.chat.id)
    lines = ["<b>锁状态</b>"]
    for item in sorted(LOCK_TYPES):
        lines.append(f"{item}: {'on' if getattr(config, item) else 'off'}")
    await message.reply("\n".join(lines), parse_mode="HTML")


@router.message(Command("ban", "tban", "tempban"))
async def ban_handler(message: Message, command: CommandObject) -> None:
    if not await require_moderation_admin(message):
        return
    if message.from_user is None:
        return

    resolved = resolve_moderation_target(message, command)
    if resolved is None:
        await message.reply("Usage: reply + /ban [minutes], /ban user_id [minutes], or private /ban chat_id user_id [minutes]")
        return
    chat_id, target_user_id, private_minutes = resolved

    minutes = max(1, min(private_minutes or parse_minutes(command, 1440), 10080))
    until_date = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    await message.bot.ban_chat_member(chat_id, target_user_id, until_date=until_date)

    async with SessionLocal() as db:
        await add_ban_sanction(db, chat_id, target_user_id, "manual_ban", minutes)
        await add_log(
            db,
            chat_id,
            message.from_user.id,
            message.from_user.username or "",
            "manual_ban",
            f"target={target_user_id}, minutes={minutes}",
        )
    await message.reply(f"User {target_user_id} banned for {minutes} minutes.")


@router.message(Command("unban"))
async def unban_handler(message: Message, command: CommandObject) -> None:
    if not await require_moderation_admin(message):
        return
    if message.from_user is None:
        return

    resolved = resolve_moderation_target(message, command)
    if resolved is None:
        await message.reply("Usage: reply + /unban, /unban user_id, or private /unban chat_id user_id")
        return
    chat_id, target_user_id, _ = resolved

    await message.bot.unban_chat_member(chat_id, target_user_id, only_if_banned=True)
    async with SessionLocal() as db:
        await mark_ban_recovered(db, chat_id, target_user_id)
        await add_log(
            db,
            chat_id,
            message.from_user.id,
            message.from_user.username or "",
            "manual_unban",
            f"target={target_user_id}",
        )
    await message.reply(f"User {target_user_id} unbanned.")


@router.message(Command("kick"))
async def kick_handler(message: Message, command: CommandObject) -> None:
    if not await require_moderation_admin(message):
        return
    if message.from_user is None:
        return

    resolved = resolve_moderation_target(message, command)
    if resolved is None:
        await message.reply("Usage: reply + /kick [minutes], /kick user_id [minutes], or private /kick chat_id user_id [minutes]")
        return
    chat_id, target_user_id, private_minutes = resolved

    minutes = max(1, min(private_minutes or parse_minutes(command, DEFAULT_KICK_MINUTES), 10080))
    until_date = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    await message.bot.ban_chat_member(chat_id, target_user_id, until_date=until_date)
    async with SessionLocal() as db:
        await add_ban_sanction(db, chat_id, target_user_id, "manual_kick", minutes)
        await add_log(
            db,
            chat_id,
            message.from_user.id,
            message.from_user.username or "",
            "manual_kick",
            f"target={target_user_id}, minutes={minutes}",
        )
    await message.reply(f"User {target_user_id} removed. They can rejoin after {minutes} minutes.")


@router.message(Command("mute", "tmute", "tempmute"))
async def mute_handler(message: Message, command: CommandObject) -> None:
    if not await require_moderation_admin(message):
        return
    if message.from_user is None:
        return

    resolved = resolve_moderation_target(message, command)
    if resolved is None:
        await message.reply("Usage: reply + /mute [minutes], /mute user_id [minutes], or private /mute chat_id user_id [minutes]")
        return
    chat_id, target_user_id, private_minutes = resolved

    minutes = max(1, min(private_minutes or parse_minutes(command, 30), 10080))
    until_date = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    await message.bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=target_user_id,
        permissions=ChatPermissions(can_send_messages=False),
        until_date=until_date,
    )
    async with SessionLocal() as db:
        await add_log(
            db,
            chat_id,
            message.from_user.id,
            message.from_user.username or "",
            "manual_mute",
            f"target={target_user_id}, minutes={minutes}",
        )
    await message.reply(f"User {target_user_id} muted for {minutes} minutes.")


@router.message(Command("unmute"))
async def unmute_handler(message: Message, command: CommandObject) -> None:
    if not await require_moderation_admin(message):
        return
    if message.from_user is None:
        return

    resolved = resolve_moderation_target(message, command)
    if resolved is None:
        await message.reply("Usage: reply + /unmute, /unmute user_id, or private /unmute chat_id user_id")
        return
    chat_id, target_user_id, _ = resolved

    await message.bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=target_user_id,
        permissions=ChatPermissions(can_send_messages=True),
    )
    async with SessionLocal() as db:
        await add_log(
            db,
            chat_id,
            message.from_user.id,
            message.from_user.username or "",
            "manual_unmute",
            f"target={target_user_id}",
        )
    await message.reply(f"User {target_user_id} unmuted.")
