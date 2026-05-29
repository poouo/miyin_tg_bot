import asyncio
from html import escape

from aiogram import Bot

NOTICE_DELETE_SECONDS = 60


def user_label(user_id: int, full_name: str = "", username: str = "") -> str:
    if full_name:
        return escape(full_name)
    if username:
        return f"@{escape(username)}"
    return escape(str(user_id))


def action_label(action: str, kick_minutes: int, mute_minutes: int, ban_minutes: int) -> str:
    if action == "ban":
        return f"拉黑 <b>{ban_minutes}</b> 分钟"
    if action == "mute":
        return f"禁言 <b>{mute_minutes}</b> 分钟"
    return f"移除群聊，<b>{kick_minutes}</b> 分钟后可重新加入"


async def delete_message_later(bot: Bot, chat_id: int, message_id: int, seconds: int = NOTICE_DELETE_SECONDS) -> None:
    await asyncio.sleep(seconds)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        return


async def send_temporary_notice(bot: Bot, chat_id: int, text: str, seconds: int = NOTICE_DELETE_SECONDS) -> None:
    sent = await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
    asyncio.create_task(delete_message_later(bot, chat_id, sent.message_id, seconds))


async def send_verify_pass_notice(bot: Bot, chat_id: int, user_id: int, full_name: str = "", username: str = "") -> None:
    label = user_label(user_id, full_name, username)
    await send_temporary_notice(
        bot,
        chat_id,
        "\n".join(
            [
                "<b>验证通过</b>",
                f"用户：<b>{label}</b>",
                f"欢迎 <b>{label}</b> 加入群聊。",
                "<i>此消息将在 1 分钟后自动撤回。</i>",
            ]
        ),
    )


async def send_verify_fail_notice(
    bot: Bot,
    chat_id: int,
    user_id: int,
    action: str,
    kick_minutes: int,
    mute_minutes: int,
    ban_minutes: int,
    full_name: str = "",
    username: str = "",
    reason: str = "未通过验证",
) -> None:
    label = user_label(user_id, full_name, username)
    action_text = action_label(action, kick_minutes, mute_minutes, ban_minutes)
    await send_temporary_notice(
        bot,
        chat_id,
        "\n".join(
            [
                "<b>验证未通过</b>",
                f"用户：<b>{label}</b>",
                f"原因：{escape(reason)}",
                f"处理：{action_text}",
                "<i>此消息将在 1 分钟后自动撤回。</i>",
            ]
        ),
    )
