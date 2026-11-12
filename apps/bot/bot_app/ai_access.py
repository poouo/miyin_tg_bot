"""Who may trigger the AI (DeepSeek) features of the bot.

Every AI answer costs API quota, so access is decided in one place:

* private chat       -> only the Telegram IDs configured as bot admins in the dashboard
* group, AI off      -> nobody (`deepseek_enabled` is the master switch)
* group, members on  -> everybody (`ai_member_enabled` is True, the default)
* group, members off -> only group admins/creator, anonymous admins and bot admin IDs
"""

from __future__ import annotations

from typing import Any

AI_ALLOWED = "ok"
AI_DISABLED = "disabled"
AI_ADMIN_ONLY = "admin_only"
AI_PRIVATE_DENIED = "private_denied"

_MANAGER_ROLES = {"administrator", "creator"}
_GROUP_CHAT_TYPES = {"group", "supergroup"}


async def _is_group_admin(message: Any) -> bool:
    chat = message.chat
    # Anonymous admins post as the group itself.
    sender_chat = getattr(message, "sender_chat", None)
    if sender_chat is not None and getattr(sender_chat, "id", None) == chat.id:
        return True
    user = message.from_user
    if user is None:
        return False
    try:
        member = await message.bot.get_chat_member(chat.id, user.id)
    except Exception:
        return False
    return getattr(member, "status", "") in _MANAGER_ROLES


async def check_ai_access(message: Any, group: Any, runtime: Any) -> str:
    """Return AI_ALLOWED, or the reason the sender may not use the AI."""
    user = message.from_user
    bot_admin_ids = set(runtime.telegram_admin_id_list)
    is_bot_admin = user is not None and user.id in bot_admin_ids

    if message.chat.type not in _GROUP_CHAT_TYPES:
        return AI_ALLOWED if is_bot_admin else AI_PRIVATE_DENIED

    if group is None or not group.deepseek_enabled:
        return AI_DISABLED
    if getattr(group, "ai_member_enabled", True):
        return AI_ALLOWED
    if is_bot_admin or await _is_group_admin(message):
        return AI_ALLOWED
    return AI_ADMIN_ONLY


AI_DENIED_TEXT = {
    AI_DISABLED: "AI is disabled in this group.",
    AI_ADMIN_ONLY: "AI 问答目前仅群管理员可用。",
    AI_PRIVATE_DENIED: "私聊 AI 仅后台配置的管理员 ID 可用，请在群里使用。",
}
