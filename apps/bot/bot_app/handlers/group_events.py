import asyncio
from datetime import datetime, timedelta, timezone
from html import escape

from aiogram import F, Router
from aiogram.types import CallbackQuery, ChatMemberUpdated, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup, Message

from apps.api.app.core.db import SessionLocal
from apps.api.app.services.chat_user_identity_service import (
    find_chat_user_ids_by_username,
    normalize_username,
    record_chat_user_identity,
)
from apps.api.app.services.community_feature_service import (
    clear_afk,
    get_afk,
    get_lock_config,
    get_log_channel,
    get_welcome_config,
    is_globally_banned,
    render_template,
    update_welcome_config,
)
from apps.api.app.services.group_service import ensure_group
from apps.api.app.services.log_service import add_log
from apps.api.app.services.auto_reply_service import match_auto_reply
from apps.api.app.services.moderation.auto_recover import get_active_ban_sanction
from apps.api.app.services.moderation.join_verification import (
    build_answer_options,
    challenge_failure_reason,
    create_challenge,
    get_challenge,
    is_challenge_answer_correct,
    is_challenge_expired,
    mark_challenge_passed,
    set_challenge_message_id,
)
from apps.api.app.services.runtime_config_service import get_runtime_config
from apps.bot.bot_app.ai_formatting import reply_ai_text
from apps.bot.bot_app.moderation_actions import ModerationActionConfig, apply_moderation_action
from apps.bot.bot_app.state import deepseek_client, policy_engine
from apps.bot.bot_app.verification_notices import (
    delete_message_later,
    send_temporary_notice,
    send_verify_fail_notice,
    send_verify_pass_notice,
)

router = Router()
MANAGER_ROLES = {"administrator", "creator"}
LOG_MESSAGE_TEXT_LIMIT = 1000
MAX_MENTION_SANCTION_TARGETS = 5

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


@router.my_chat_member(F.chat.type.in_({"group", "supergroup"}))
async def bot_membership_handler(event: ChatMemberUpdated) -> None:
    status = getattr(event.new_chat_member, "status", "")
    if status in {"left", "kicked"}:
        return

    async with SessionLocal() as db:
        await ensure_group(db, event.chat.id, event.chat.title or "")
        await add_log(
            db,
            event.chat.id,
            0,
            "",
            "group_registered",
            f"bot_status={status}",
        )


def _build_verify_keyboard(target_user_id: int, options: list[str]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for option in options:
        row.append(
            InlineKeyboardButton(
                text=option,
                callback_data=f"verify:{target_user_id}:{option}",
            )
        )
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append(
        [
            InlineKeyboardButton(text="通过", callback_data=f"verify_pass:{target_user_id}"),
            InlineKeyboardButton(text="移除", callback_data=f"verify_remove:{target_user_id}"),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _delete_verification_message(bot, chat_id: int, challenge) -> None:
    message_id = int(getattr(challenge, "message_id", 0) or 0)
    if message_id <= 0:
        return
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception:
        return


async def _delete_message_later(bot, chat_id: int, message_id: int, seconds: int) -> None:
    await delete_message_later(bot, chat_id, message_id, seconds)


async def _is_group_manager(message: Message) -> bool:
    if message.from_user is None:
        return False
    try:
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
    except Exception:
        return False
    return getattr(member, "status", "") in MANAGER_ROLES


async def _is_callback_group_manager(callback: CallbackQuery) -> bool:
    if callback.message is None or callback.from_user is None:
        return False
    try:
        member = await callback.bot.get_chat_member(callback.message.chat.id, callback.from_user.id)
    except Exception:
        return False
    return getattr(member, "status", "") in MANAGER_ROLES


async def _eligible_mentioned_member(message: Message, user_id: int, expected_username: str = "") -> tuple[int, str] | None:
    sender_id = message.from_user.id if message.from_user else 0
    bot_id = getattr(message.bot, "id", 0)
    if user_id in {sender_id, bot_id}:
        return None

    try:
        member = await message.bot.get_chat_member(message.chat.id, user_id)
    except Exception:
        return None

    status = getattr(member, "status", "")
    if status in MANAGER_ROLES or status in {"left", "kicked"}:
        return None
    target_user = getattr(member, "user", None)
    if target_user is None or target_user.id != user_id:
        return None
    if status == "restricted" and not getattr(member, "is_member", True):
        return None
    if expected_username and normalize_username(target_user.username) != expected_username:
        return None
    return target_user.id, target_user.username or ""


async def _resolve_mentioned_sanction_targets(message: Message, db) -> list[tuple[int, str]]:
    targets: list[tuple[int, str]] = []
    seen_user_ids = {message.from_user.id} if message.from_user else set()

    async def add_target(user_id: int, expected_username: str = "") -> None:
        if len(targets) >= MAX_MENTION_SANCTION_TARGETS or user_id in seen_user_ids:
            return
        candidate = await _eligible_mentioned_member(message, user_id, expected_username)
        if candidate is None:
            return
        seen_user_ids.add(candidate[0])
        targets.append(candidate)

    for entity in message.entities or []:
        entity_type = getattr(getattr(entity, "type", ""), "value", getattr(entity, "type", ""))
        if entity_type != "text_mention":
            continue
        target_user = getattr(entity, "user", None)
        if target_user is not None:
            await add_target(target_user.id)
        if len(targets) >= MAX_MENTION_SANCTION_TARGETS:
            return targets

    mentioned_usernames: list[str] = []
    seen_usernames: set[str] = set()
    for entity in message.entities or []:
        entity_type = getattr(getattr(entity, "type", ""), "value", getattr(entity, "type", ""))
        if entity_type != "mention":
            continue
        try:
            entity_text = entity.extract_from(message.text or "")
        except (AttributeError, TypeError, ValueError):
            continue
        normalized_username = normalize_username(entity_text)
        if normalized_username and normalized_username not in seen_usernames:
            seen_usernames.add(normalized_username)
            mentioned_usernames.append(normalized_username)
        if len(mentioned_usernames) >= MAX_MENTION_SANCTION_TARGETS:
            break

    for username in mentioned_usernames:
        user_ids = await find_chat_user_ids_by_username(db, message.chat.id, username)
        for user_id in user_ids:
            await add_target(user_id, username)
            if len(targets) >= MAX_MENTION_SANCTION_TARGETS:
                return targets
    return targets


async def _apply_mention_sanctions(
    message: Message,
    db,
    reason: str,
    action_config: ModerationActionConfig,
) -> None:
    if action_config.action not in {"kick", "mute", "ban"}:
        return

    for user_id, username in await _resolve_mentioned_sanction_targets(message, db):
        try:
            await apply_moderation_action(
                message.bot,
                db,
                message.chat.id,
                user_id,
                username,
                f"{reason}:mentioned_by:{message.from_user.id}"[:255],
                action_config,
            )
        except Exception:
            continue


def _message_lock_type(message: Message) -> str | None:
    text = message.text or message.caption or ""
    entities = list(message.entities or []) + list(message.caption_entities or [])
    if text.startswith("/"):
        return "commands"
    if getattr(message, "forward_origin", None) or getattr(message, "forward_date", None):
        return "forwards"
    if getattr(message, "sticker", None):
        return "stickers"
    if (
        getattr(message, "photo", None)
        or getattr(message, "video", None)
        or getattr(message, "animation", None)
        or getattr(message, "document", None)
        or getattr(message, "audio", None)
        or getattr(message, "voice", None)
    ):
        return "media"
    if any(item.type in {"url", "text_link"} for item in entities):
        return "links"
    lowered = text.lower()
    if "http://" in lowered or "https://" in lowered or "t.me/" in lowered:
        return "links"
    return None


async def _enforce_locks(message: Message, db) -> bool:
    if await _is_group_manager(message):
        return False
    lock_type = _message_lock_type(message)
    if lock_type is None:
        return False
    config = await get_lock_config(db, message.chat.id)
    if not getattr(config, lock_type):
        return False
    try:
        await message.delete()
    except Exception:
        pass
    await add_log(db, message.chat.id, message.from_user.id if message.from_user else 0, "", "lock_deleted", lock_type)
    return True


async def _send_log_channel(bot, db, chat_id: int, text: str) -> None:
    config = await get_log_channel(db, chat_id)
    if not config.enabled or not config.log_chat_id:
        return
    try:
        await bot.send_message(config.log_chat_id, text, parse_mode="HTML")
    except Exception:
        return


async def _approve_verified_member(
    bot,
    db,
    chat_id: int,
    user_id: int,
    challenge,
    full_name: str = "",
    username: str = "",
    detail: str = "button",
) -> None:
    if challenge is not None:
        await _delete_verification_message(bot, chat_id, challenge)
        challenge.message_id = 0
    await bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=MEMBER_UNRESTRICT_PERMISSIONS,
    )
    await add_log(db, chat_id, user_id, username, "join_verify_passed", detail)
    try:
        await send_verify_pass_notice(bot, chat_id, user_id, full_name, username)
    except Exception:
        pass


async def _remove_unverified_member(
    bot,
    db,
    chat_id: int,
    user_id: int,
    admin_id: int,
    challenge,
) -> None:
    if challenge is not None:
        await _delete_verification_message(bot, chat_id, challenge)
        challenge.passed = True
        challenge.message_id = 0
    await bot.ban_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        until_date=datetime.now(timezone.utc) + timedelta(minutes=1),
    )
    await add_log(db, chat_id, user_id, "", "join_verify_failed", f"admin_remove:{admin_id}")
    await db.commit()


async def _handle_afk(message: Message, db) -> None:
    if message.from_user is None:
        return
    cleared = await clear_afk(db, message.from_user.id)
    if cleared:
        try:
            await message.reply("欢迎回来，AFK 状态已解除。")
        except Exception:
            pass

    candidates: dict[int, str] = {}
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
        candidates[user.id] = user.full_name
    for entity in message.entities or []:
        user = getattr(entity, "user", None)
        if user:
            candidates[user.id] = user.full_name
    for user_id, full_name in candidates.items():
        afk = await get_afk(db, user_id)
        if afk is None:
            continue
        reason = f"\n原因：{escape(afk.reason)}" if afk.reason else ""
        try:
            await message.reply(f"<b>{escape(full_name)}</b> 当前 AFK。{reason}", parse_mode="HTML")
        except Exception:
            pass


def _log_message_detail(reason: str, text: str) -> str:
    normalized_text = " ".join((text or "").split())
    if len(normalized_text) > LOG_MESSAGE_TEXT_LIMIT:
        normalized_text = f"{normalized_text[:LOG_MESSAGE_TEXT_LIMIT]}..."
    if not normalized_text:
        return reason
    return f"reason={reason}\nmessage={normalized_text}"


@router.message(
    F.chat.type.in_({"group", "supergroup"}),
    ~F.text,
    ~F.new_chat_members,
    ~F.left_chat_member,
)
async def group_non_text_lock_handler(message: Message) -> None:
    if message.from_user is None or message.from_user.is_bot:
        return
    async with SessionLocal() as db:
        await ensure_group(db, message.chat.id, message.chat.title or "")
        await record_chat_user_identity(db, message.chat.id, message.from_user.id, message.from_user.username)
        await _enforce_locks(message, db)


@router.message(F.chat.type.in_({"group", "supergroup"}), F.new_chat_members)
async def new_member_handler(message: Message) -> None:
    chat = message.chat
    if not message.new_chat_members:
        return

    async with SessionLocal() as db:
        for member in message.new_chat_members:
            await record_chat_user_identity(db, chat.id, member.id, member.username)
        runtime = await get_runtime_config(db)
        group = await ensure_group(db, chat.id, chat.title or "")
        welcome_config = await get_welcome_config(db, chat.id)
        if not group.join_verification_enabled:
            for member in message.new_chat_members:
                if member.is_bot:
                    continue
                gban = await is_globally_banned(db, member.id)
                if gban:
                    try:
                        await message.bot.ban_chat_member(chat.id, member.id)
                    except Exception:
                        pass
                    await add_log(db, chat.id, member.id, member.username or "", "global_ban_enforced", gban.reason)
                    await _send_log_channel(
                        message.bot,
                        db,
                        chat.id,
                        f"<b>全局封禁拦截</b>\n用户：<code>{member.id}</code>\n原因：{escape(gban.reason or '')}",
                    )
                    continue
                if welcome_config.welcome_enabled:
                    if welcome_config.clean_welcome and welcome_config.last_welcome_message_id:
                        try:
                            await message.bot.delete_message(chat.id, welcome_config.last_welcome_message_id)
                        except Exception:
                            pass
                    try:
                        text = render_template(
                            welcome_config.welcome_text,
                            chat_title=chat.title or "",
                            user_id=member.id,
                            full_name=member.full_name,
                            username=member.username or "",
                        )
                    except Exception:
                        text = f"欢迎 {escape(member.full_name)} 加入 {escape(chat.title or '')}。"
                    sent = await message.answer(text, parse_mode="HTML")
                    await update_welcome_config(db, chat.id, last_welcome_message_id=sent.message_id)
                await add_log(db, chat.id, member.id, member.username or "", "member_joined", member.full_name)
            return

        for member in message.new_chat_members:
            if member.is_bot:
                continue
            gban = await is_globally_banned(db, member.id)
            if gban:
                try:
                    await message.bot.ban_chat_member(chat.id, member.id)
                except Exception:
                    pass
                await add_log(db, chat.id, member.id, member.username or "", "global_ban_enforced", gban.reason)
                await _send_log_channel(
                    message.bot,
                    db,
                    chat.id,
                    f"<b>全局封禁拦截</b>\n用户：<code>{member.id}</code>\n原因：{escape(gban.reason or '')}",
                )
                continue
            await add_log(
                db,
                chat.id,
                member.id,
                member.username or "",
                "member_joined",
                member.full_name,
            )
            if welcome_config.welcome_enabled:
                if welcome_config.clean_welcome and welcome_config.last_welcome_message_id:
                    try:
                        await message.bot.delete_message(chat.id, welcome_config.last_welcome_message_id)
                    except Exception:
                        pass
                try:
                    welcome_text = render_template(
                        welcome_config.welcome_text,
                        chat_title=chat.title or "",
                        user_id=member.id,
                        full_name=member.full_name,
                        username=member.username or "",
                    )
                    sent = await message.answer(welcome_text, parse_mode="HTML")
                    await update_welcome_config(db, chat.id, last_welcome_message_id=sent.message_id)
                except Exception:
                    pass
            await message.bot.restrict_chat_member(
                chat_id=chat.id,
                user_id=member.id,
                permissions=ChatPermissions(can_send_messages=False),
            )
            challenge = await create_challenge(db, chat.id, member.id)
            options = build_answer_options(challenge.answer)
            verify_message = await message.answer(
                "\n".join(
                    [
                        "<b>入群验证</b>",
                        f"欢迎 <b>{escape(member.full_name)}</b>",
                        f"请在 <b>{runtime.join_verify_timeout_sec}</b> 秒内完成验证。",
                        "",
                        f"<code>{escape(challenge.question)}</code>",
                        "",
                        "请点击下方按钮选择答案。",
                    ]
                ),
                parse_mode="HTML",
                reply_markup=_build_verify_keyboard(member.id, options),
            )
            await set_challenge_message_id(db, chat.id, member.id, verify_message.message_id)
            await add_log(db, chat.id, member.id, member.username or "", "join_verify_created", challenge.question)
            await _send_log_channel(
                message.bot,
                db,
                chat.id,
                f"<b>新成员入群</b>\n用户：<code>{member.id}</code>\n名称：{escape(member.full_name)}",
            )


@router.message(F.chat.type.in_({"group", "supergroup"}), F.left_chat_member)
async def left_member_handler(message: Message) -> None:
    if message.left_chat_member is None:
        return
    member = message.left_chat_member
    if member.is_bot:
        return

    async with SessionLocal() as db:
        await ensure_group(db, message.chat.id, message.chat.title or "")
        if await get_active_ban_sanction(db, message.chat.id, member.id):
            return
        await add_log(
            db,
            message.chat.id,
            member.id,
            member.username or "",
            "member_left",
            member.full_name,
        )
        config = await get_welcome_config(db, message.chat.id)
        if config.goodbye_enabled:
            try:
                text = render_template(
                    config.goodbye_text,
                    chat_title=message.chat.title or "",
                    user_id=member.id,
                    full_name=member.full_name,
                    username=member.username or "",
                )
            except Exception:
                text = f"{escape(member.full_name)} 离开了 {escape(message.chat.title or '')}。"
            try:
                await message.answer(text, parse_mode="HTML")
            except Exception:
                pass
        await _send_log_channel(
            message.bot,
            db,
            message.chat.id,
            f"<b>成员退群</b>\n用户：<code>{member.id}</code>\n名称：{escape(member.full_name)}",
        )


@router.callback_query(F.data.startswith("verify:"))
async def verify_button_handler(callback: CallbackQuery) -> None:
    if callback.message is None or callback.from_user is None:
        return

    parts = (callback.data or "").split(":", 2)
    if len(parts) != 3:
        await callback.answer("验证数据无效", show_alert=True)
        return

    _, target_user_id_raw, selected_answer = parts
    try:
        target_user_id = int(target_user_id_raw)
    except ValueError:
        await callback.answer("验证数据无效", show_alert=True)
        return

    if callback.from_user.id != target_user_id:
        await callback.answer("仅该新成员可点击验证按钮", show_alert=True)
        return

    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    async with SessionLocal() as db:
        group = await ensure_group(db, chat_id, callback.message.chat.title or "")
        challenge = await get_challenge(db, chat_id, user_id)
        if not is_challenge_answer_correct(challenge, selected_answer):
            fail_reason = challenge_failure_reason(challenge, selected_answer)
            if challenge is not None and not challenge.passed:
                await _delete_verification_message(callback.bot, chat_id, challenge)
                action_config = ModerationActionConfig(
                    action=group.join_verify_fail_action,
                    kick_minutes=group.join_verify_fail_kick_minutes,
                    mute_minutes=group.join_verify_fail_mute_minutes,
                    ban_minutes=group.join_verify_fail_ban_minutes,
                )
                await apply_moderation_action(
                    callback.bot,
                    db,
                    chat_id,
                    user_id,
                    callback.from_user.username or "",
                    "join_verify_failed",
                    action_config,
                )
                await send_verify_fail_notice(
                    callback.bot,
                    chat_id,
                    user_id,
                    action_config.action,
                    action_config.kick_minutes,
                    action_config.mute_minutes,
                    action_config.ban_minutes,
                    callback.from_user.full_name,
                    callback.from_user.username or "",
                    fail_reason,
                )
                challenge.passed = True
                challenge.message_id = 0
            else:
                await send_temporary_notice(callback.bot, chat_id, f"验证失败：{fail_reason}")
            await add_log(db, chat_id, user_id, callback.from_user.username or "", "join_verify_failed", fail_reason)
            await callback.answer(f"验证失败：{fail_reason}", show_alert=True)
            return

        await _approve_verified_member(
            callback.bot,
            db,
            chat_id,
            user_id,
            challenge,
            callback.from_user.full_name,
            callback.from_user.username or "",
            "button",
        )
        await mark_challenge_passed(db, challenge)

    await callback.answer("验证通过，欢迎加入！")


@router.callback_query(F.data.startswith("verify_pass:"))
async def verify_admin_pass_handler(callback: CallbackQuery) -> None:
    if callback.message is None or callback.from_user is None:
        return

    parts = (callback.data or "").split(":", 1)
    if len(parts) != 2:
        await callback.answer("验证数据无效", show_alert=True)
        return

    try:
        target_user_id = int(parts[1])
    except ValueError:
        await callback.answer("验证数据无效", show_alert=True)
        return

    if not await _is_callback_group_manager(callback):
        await callback.answer("仅群管理员可直接通过验证", show_alert=True)
        return

    chat_id = callback.message.chat.id
    async with SessionLocal() as db:
        await ensure_group(db, chat_id, callback.message.chat.title or "")
        challenge = await get_challenge(db, chat_id, target_user_id)
        if challenge is None or challenge.passed or is_challenge_expired(challenge):
            fail_reason = challenge_failure_reason(challenge, "")
            await callback.answer(f"无法通过：{fail_reason}", show_alert=True)
            return

        await _approve_verified_member(
            callback.bot,
            db,
            chat_id,
            target_user_id,
            challenge,
            detail=f"admin:{callback.from_user.id}",
        )
        await mark_challenge_passed(db, challenge)

    await callback.answer("已由管理员通过验证")


@router.callback_query(F.data.startswith("verify_remove:"))
async def verify_admin_remove_handler(callback: CallbackQuery) -> None:
    if callback.message is None or callback.from_user is None:
        return

    parts = (callback.data or "").split(":", 1)
    if len(parts) != 2:
        await callback.answer("验证数据无效", show_alert=True)
        return

    try:
        target_user_id = int(parts[1])
    except ValueError:
        await callback.answer("验证数据无效", show_alert=True)
        return

    if not await _is_callback_group_manager(callback):
        await callback.answer("仅群管理员可移除验证用户", show_alert=True)
        return

    chat_id = callback.message.chat.id
    async with SessionLocal() as db:
        await ensure_group(db, chat_id, callback.message.chat.title or "")
        challenge = await get_challenge(db, chat_id, target_user_id)
        if challenge is None:
            await callback.answer("验证记录不存在", show_alert=True)
            return
        if challenge.passed:
            await callback.answer("验证已处理", show_alert=True)
            return

        await _remove_unverified_member(
            callback.bot,
            db,
            chat_id,
            target_user_id,
            callback.from_user.id,
            challenge,
        )

    await callback.answer("已移除该用户")


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
        await record_chat_user_identity(db, chat.id, user.id, user.username)
        gban = await is_globally_banned(db, user.id)
        if gban:
            try:
                await message.bot.ban_chat_member(chat.id, user.id)
            except Exception:
                pass
            try:
                await message.delete()
            except Exception:
                pass
            await add_log(db, chat.id, user.id, user.username or "", "global_ban_enforced", gban.reason)
            await _send_log_channel(
                message.bot,
                db,
                chat.id,
                f"<b>全局封禁执行</b>\n用户：<code>{user.id}</code>\n原因：{escape(gban.reason or '')}",
            )
            return
        await _handle_afk(message, db)
        if await _enforce_locks(message, db):
            return
        is_manager = await _is_group_manager(message)
        decision = None if is_manager else await policy_engine.check_message(db, chat.id, user.id, text)
        if decision is not None and decision.blocked:
            should_delete_message = (
                (
                    decision.reason == "keyword_filter"
                    and (
                        decision.keyword_rule.delete_message
                        if decision.keyword_rule is not None
                        else True
                    )
                )
                or (
                    decision.reason == "ad_block"
                    and (
                        decision.ad_keyword_rule.delete_message
                        if decision.ad_keyword_rule is not None
                        else group.ad_block_delete_message
                    )
                )
                or (decision.reason == "anti_spam" and group.anti_spam_delete_message)
            )
            if should_delete_message:
                try:
                    await message.delete()
                except Exception:
                    pass

            reason = decision.reason
            if decision.keyword_rule is not None:
                keyword_rule = decision.keyword_rule
                reason = f"keyword_filter:{keyword_rule.keyword}"
                if keyword_rule.ban_user or keyword_rule.mute_user:
                    await apply_moderation_action(
                        message.bot,
                        db,
                        chat.id,
                        user.id,
                        user.username or "",
                        reason,
                        ModerationActionConfig(
                            action="ban" if keyword_rule.ban_user else "mute",
                            kick_minutes=1,
                            mute_minutes=keyword_rule.mute_minutes,
                            ban_minutes=keyword_rule.ban_minutes,
                        ),
                    )
            elif decision.reason == "ad_block":
                if decision.ad_keyword_rule is not None:
                    ad_keyword_rule = decision.ad_keyword_rule
                    reason = f"ad_block:{ad_keyword_rule.keyword}"
                    if ad_keyword_rule.ban_user or ad_keyword_rule.mute_user:
                        action_config = ModerationActionConfig(
                            action="ban" if ad_keyword_rule.ban_user else "mute",
                            kick_minutes=1,
                            mute_minutes=ad_keyword_rule.mute_minutes,
                            ban_minutes=ad_keyword_rule.ban_minutes,
                        )
                        await apply_moderation_action(
                            message.bot,
                            db,
                            chat.id,
                            user.id,
                            user.username or "",
                            reason,
                            action_config,
                        )
                        if ad_keyword_rule.apply_to_mentions:
                            await _apply_mention_sanctions(message, db, reason, action_config)
                else:
                    action_config = ModerationActionConfig(
                        action=group.ad_block_action,
                        kick_minutes=group.ad_block_kick_minutes,
                        mute_minutes=group.ad_block_mute_minutes,
                        ban_minutes=group.ad_block_ban_minutes,
                    )
                    await apply_moderation_action(
                        message.bot,
                        db,
                        chat.id,
                        user.id,
                        user.username or "",
                        reason,
                        action_config,
                    )
                    if group.ad_block_apply_to_mentions:
                        await _apply_mention_sanctions(message, db, reason, action_config)
            elif decision.reason == "anti_spam":
                await apply_moderation_action(
                    message.bot,
                    db,
                    chat.id,
                    user.id,
                    user.username or "",
                    reason,
                    ModerationActionConfig(
                        action=group.anti_spam_action,
                        kick_minutes=group.anti_spam_kick_minutes,
                        mute_minutes=group.anti_spam_mute_minutes,
                        ban_minutes=group.anti_spam_ban_minutes,
                    ),
                )
            await add_log(db, chat.id, user.id, user.username or "", "message_blocked", _log_message_detail(reason, text))
            return

        if group.auto_recover_enabled:
            auto_reply = await match_auto_reply(db, chat.id, text)
            if auto_reply:
                reply_text = auto_reply.reply_text[:3800]
                parse_mode = (getattr(auto_reply, "parse_mode", "plain") or "plain").lower()
                reply_kwargs: dict = {}
                if parse_mode == "markdownv2":
                    reply_kwargs["parse_mode"] = "MarkdownV2"
                elif parse_mode == "html":
                    reply_kwargs["parse_mode"] = "HTML"
                try:
                    sent = await message.reply(reply_text, **reply_kwargs)
                except Exception:
                    # Fallback to plain text when format content is invalid.
                    sent = await message.reply(reply_text)
                await add_log(
                    db,
                    chat.id,
                    user.id,
                    user.username or "",
                    "auto_reply_triggered",
                    auto_reply.keyword,
                )
                if auto_reply.delete_after_seconds > 0:
                    asyncio.create_task(
                        _delete_message_later(
                            message.bot,
                            chat.id,
                            sent.message_id,
                            auto_reply.delete_after_seconds,
                        )
                    )
                return

        bot_mention = runtime.telegram_bot_username.strip()
        has_mention = bool(bot_mention) and f"@{bot_mention.lower()}" in text.lower()
        if group.deepseek_enabled and (has_mention or text.startswith("问:")):
            question = text.replace(f"@{bot_mention}", "").strip() if bot_mention else text.strip()
            if question.startswith("问:"):
                question = question[2:].strip()
            if question:
                answer = await deepseek_client.ask(question, db=db)
                sent = await reply_ai_text(message, answer)
                delete_after_seconds = int(getattr(group, "ai_reply_delete_after_seconds", 0) or 0)
                if sent is not None and delete_after_seconds > 0:
                    asyncio.create_task(
                        _delete_message_later(
                            message.bot,
                            chat.id,
                            sent.message_id,
                            delete_after_seconds,
                        )
                    )
