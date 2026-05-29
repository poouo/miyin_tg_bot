import asyncio
import xml.etree.ElementTree as ET

from aiogram import Bot
from aiogram.types import ChatPermissions
import httpx

from apps.api.app.core.db import SessionLocal
from apps.api.app.services.community_feature_service import list_all_rss_subscriptions, update_rss_last_entry
from apps.api.app.services.group_service import ensure_group
from apps.api.app.services.log_service import add_log
from apps.api.app.services.moderation.auto_recover import list_recoverable_sanctions, mark_recovered
from apps.api.app.services.moderation.join_verification import list_expired_unpassed
from apps.bot.bot_app.moderation_actions import ModerationActionConfig, apply_moderation_action
from apps.bot.bot_app.verification_notices import send_verify_fail_notice


def _xml_text(node: ET.Element, names: list[str]) -> str:
    for name in names:
        found = node.find(name)
        if found is not None and found.text:
            return found.text.strip()
    return ""


def _parse_feed_items(raw: str) -> tuple[str, list[dict[str, str]]]:
    root = ET.fromstring(raw)
    channel = root.find("channel")
    if channel is not None:
        feed_title = _xml_text(channel, ["title"])
        items = []
        for item in channel.findall("item")[:5]:
            title = _xml_text(item, ["title"])
            link = _xml_text(item, ["link"])
            entry_id = _xml_text(item, ["guid", "id"]) or link or title
            if entry_id:
                items.append({"id": entry_id, "title": title, "link": link})
        return feed_title, items

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    feed_title = _xml_text(root, ["{http://www.w3.org/2005/Atom}title", "title"])
    items = []
    for entry in root.findall("atom:entry", ns)[:5] + root.findall("entry")[:5]:
        title = _xml_text(entry, ["{http://www.w3.org/2005/Atom}title", "title"])
        entry_id = _xml_text(entry, ["{http://www.w3.org/2005/Atom}id", "id"]) or title
        link = ""
        link_node = entry.find("atom:link", ns) or entry.find("link")
        if link_node is not None:
            link = link_node.attrib.get("href", "") or (link_node.text or "").strip()
        if entry_id:
            items.append({"id": entry_id, "title": title, "link": link})
    return feed_title, items[:5]


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
                    group = await ensure_group(db, challenge.chat_id, "")
                    action_config = ModerationActionConfig(
                        action=group.join_verify_fail_action,
                        kick_minutes=group.join_verify_fail_kick_minutes,
                        mute_minutes=group.join_verify_fail_mute_minutes,
                        ban_minutes=group.join_verify_fail_ban_minutes,
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
                    await send_verify_fail_notice(
                        bot,
                        challenge.chat_id,
                        challenge.user_id,
                        action_config.action,
                        action_config.kick_minutes,
                        action_config.mute_minutes,
                        action_config.ban_minutes,
                        reason="验证超时",
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


async def rss_poll_task(bot: Bot) -> None:
    while True:
        try:
            async with SessionLocal() as db:
                subscriptions = await list_all_rss_subscriptions(db)
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                for sub in subscriptions:
                    try:
                        response = await client.get(sub.url)
                        response.raise_for_status()
                        feed_title, items = _parse_feed_items(response.text)
                    except Exception:
                        continue
                    if not items:
                        continue
                    latest = items[0]
                    latest_id = latest["id"]
                    if not sub.last_entry_id:
                        async with SessionLocal() as db:
                            await update_rss_last_entry(db, sub.id, latest_id, feed_title)
                        continue
                    if latest_id == sub.last_entry_id:
                        continue
                    title = latest["title"] or feed_title or "RSS 更新"
                    link = latest["link"]
                    text = f"<b>{title}</b>"
                    if link:
                        text += f"\n{link}"
                    try:
                        await bot.send_message(sub.chat_id, text, parse_mode="HTML", disable_web_page_preview=False)
                    except Exception:
                        pass
                    async with SessionLocal() as db:
                        await update_rss_last_entry(db, sub.id, latest_id, feed_title)
        except Exception:
            pass
        await asyncio.sleep(300)
