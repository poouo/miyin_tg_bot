import asyncio
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import escape

from aiogram import Bot
import httpx

from apps.api.app.core.db import SessionLocal
from apps.api.app.models.entities import RssSubscription
from apps.api.app.services.community_feature_service import list_all_rss_subscriptions, update_rss_last_entry
from apps.api.app.services.group_service import ensure_group, get_group
from apps.api.app.services.log_service import add_log
from apps.api.app.services.moderation.auto_recover import list_recoverable_sanctions, mark_recovered
from apps.api.app.services.moderation.join_verification import list_expired_unpassed
from apps.bot.bot_app.ai_ad_guard import BufferedMessage, ai_ad_guard, clear_expired_mention_warnings, handle_ai_ad_batch
from apps.bot.bot_app.moderation_actions import ModerationActionConfig, apply_moderation_action
from apps.bot.bot_app.verification_notices import send_verify_fail_notice

logger = logging.getLogger(__name__)


def _xml_text(node: ET.Element, names: list[str]) -> str:
    for name in names:
        found = node.find(name)
        if found is not None and found.text:
            return found.text.strip()
    return ""


def _feed_date(value: str) -> datetime | None:
    if not value:
        return None
    try:
        date = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            date = parsedate_to_datetime(value)
        except (ValueError, TypeError):
            return None
    return date if date.tzinfo else date.replace(tzinfo=timezone.utc)


def _latest_first(items: list[dict[str, str]]) -> list[dict[str, str]]:
    dates = [_feed_date(item["published"]) for item in items]
    if all(date is not None for date in dates):
        return [items[index] for index in sorted(range(len(items)), key=dates.__getitem__, reverse=True)]
    return items


def _parse_feed_items(raw: str) -> tuple[str, list[dict[str, str]]]:
    root = ET.fromstring(raw)
    channel = root.find("channel")
    if channel is not None:
        feed_title = _xml_text(channel, ["title"])
        items = []
        for item in channel.findall("item"):
            title = _xml_text(item, ["title"])
            link = _xml_text(item, ["link"])
            entry_id = _xml_text(item, ["guid", "id"]) or link or title
            if entry_id:
                items.append({"id": entry_id, "title": title, "link": link, "published": _xml_text(item, ["pubDate"])})
        return feed_title, _latest_first(items)

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    feed_title = _xml_text(root, ["{http://www.w3.org/2005/Atom}title", "title"])
    items = []
    for entry in root.findall("atom:entry", ns) + root.findall("entry"):
        title = _xml_text(entry, ["{http://www.w3.org/2005/Atom}title", "title"])
        entry_id = _xml_text(entry, ["{http://www.w3.org/2005/Atom}id", "id"]) or title
        link = ""
        link_node = entry.find("atom:link", ns)
        if link_node is None:
            link_node = entry.find("link")
        if link_node is not None:
            link = link_node.attrib.get("href", "") or (link_node.text or "").strip()
        if entry_id:
            published = _xml_text(entry, ["{http://www.w3.org/2005/Atom}published", "{http://www.w3.org/2005/Atom}updated", "updated"])
            items.append({"id": entry_id, "title": title, "link": link, "published": published})
    return feed_title, _latest_first(items)


async def recover_mute_task(bot: Bot) -> None:
    while True:
        try:
            async with SessionLocal() as db:
                sanctions = await list_recoverable_sanctions(db)
                for item in sanctions:
                    # Telegram expires timed restrictions. A new restriction may already be in effect.
                    await mark_recovered(db, item.id)
                    await add_log(db, item.chat_id, item.user_id, "", "auto_recover", item.reason)
        except Exception:
            logger.exception("Could not reconcile expired timed restrictions")
        await asyncio.sleep(20)


async def _delete_verification_message(bot: Bot, chat_id: int, message_id: int) -> None:
    if message_id <= 0:
        return
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception:
        return


async def kick_unverified_task(bot: Bot) -> None:
    while True:
        try:
            async with SessionLocal() as db:
                items = await list_expired_unpassed(db)
                for challenge in items:
                    group = await ensure_group(db, challenge.chat_id, "")
                    await _delete_verification_message(
                        bot,
                        challenge.chat_id,
                        int(getattr(challenge, "message_id", 0) or 0),
                    )
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
                    challenge.message_id = 0
                await db.commit()
        except Exception:
            pass
        await asyncio.sleep(15)


async def _deliver_rss_items(bot: Bot, sub: RssSubscription, feed_title: str, items: list[dict[str, str]]) -> None:
    if not sub.last_entry_id:
        async with SessionLocal() as db:
            await update_rss_last_entry(db, sub.id, items[0]["id"], feed_title)
        return
    pending = []
    for item in items:
        if item["id"] == sub.last_entry_id:
            break
        pending.append(item)
    for item in reversed(pending):
        title = escape((item["title"] or feed_title or "RSS 更新")[:1000])
        link = escape(item["link"][:2000])
        text = f"<b>{title}</b>" + (f"\n{link}" if link else "")
        try:
            await bot.send_message(sub.chat_id, text, parse_mode="HTML", disable_web_page_preview=False)
        except Exception:
            logger.warning("RSS delivery failed for subscription %s", sub.id, exc_info=True)
            break
        async with SessionLocal() as db:
            await update_rss_last_entry(db, sub.id, item["id"], feed_title)


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
                    await _deliver_rss_items(bot, sub, feed_title, items)
        except Exception:
            logger.exception("RSS polling failed")
        await asyncio.sleep(300)


async def _handle_ai_ad_batch(bot: Bot, chat_id: int, batch: list[BufferedMessage]) -> None:
    try:
        async with SessionLocal() as db:
            group = await get_group(db, chat_id)
            if group is not None and group.ai_ad_block_enabled:
                await handle_ai_ad_batch(bot, db, group, batch)
    except Exception:
        logger.warning("AI ad batch handling failed for chat %s", chat_id, exc_info=True)


async def ai_ad_flush_task(bot: Bot) -> None:
    concurrent_groups = 4
    loop = asyncio.get_running_loop()
    cleanup_at = 0.0
    in_flight: dict[int, asyncio.Task] = {}
    try:
        while True:
            in_flight = {chat_id: task for chat_id, task in in_flight.items() if not task.done()}
            for chat_id, batch in ai_ad_guard.take_ready(
                exclude=set(in_flight), limit=concurrent_groups - len(in_flight),
            ):
                in_flight[chat_id] = asyncio.create_task(_handle_ai_ad_batch(bot, chat_id, batch))
            now = loop.time()
            if now >= cleanup_at:
                cleanup_at = now + 3600
                try:
                    async with SessionLocal() as db:
                        await clear_expired_mention_warnings(db)
                except Exception:
                    logger.warning("Could not clear expired ad request warnings", exc_info=True)
            await asyncio.sleep(1)
    finally:
        for task in in_flight.values():
            task.cancel()
        await asyncio.gather(*in_flight.values(), return_exceptions=True)
