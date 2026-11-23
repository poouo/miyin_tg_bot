"""AI assisted ad detection for group chat.

Regex and keyword rules only catch known patterns. This module buffers normal
group messages for a configurable window (1-60s), asks the AI once per window
which of them are ads, and applies a confidence tiered moderation action:

    confidence >= high threshold   -> high action   (default ban)
    confidence >= mid threshold    -> mid action    (default mute)
    confidence >= min threshold    -> min action    (default delete + warn)
    below the min threshold        -> ignored

Batching keeps API usage low and catches ads whose wording keeps changing.
"""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.models.entities import GroupConfig
from apps.api.app.services.community_feature_service import add_warning, reset_warnings
from apps.api.app.services.log_service import add_log
from apps.api.app.services.runtime_config_service import get_runtime_config
from apps.bot.bot_app.moderation_actions import (
    DEFAULT_KICK_MINUTES,
    ModerationActionConfig,
    apply_moderation_action,
)
from apps.bot.bot_app.state import deepseek_client

logger = logging.getLogger(__name__)

MAX_BATCH_MESSAGES = 40
MAX_MESSAGE_CHARS = 300
MAX_REASON_CHARS = 80
MIN_CONFIDENCE = 60
DEFAULT_WINDOW_SEC = 60
MIN_WINDOW_SEC = 1
MAX_WINDOW_SEC = 60
MENTION_MEMORY_SEC = 120
MENTION_MEMORY_MAX = 60
AI_AD_EVENT = "ai_ad_block"
VALID_AI_AD_ACTIONS = {"delete", "warn", "mute", "kick", "ban"}
ACTION_SEVERITY = {"delete": 1, "warn": 2, "mute": 3, "kick": 4, "ban": 5}
WARN_ACTION_LABELS = {"mute": "禁言", "kick": "移出群聊", "ban": "封禁"}

AI_AD_SYSTEM_PROMPT = (
    "你是 Telegram 群聊的广告识别助手。用户会给你一个 JSON 数组，元素是群聊消息，"
    "包含 id、sender、text 字段。请判断其中哪些消息属于广告或推广引流，例如："
    "推销商品或服务、拉人进群或加私聊、返利刷单兼职、博彩色情、贷款理财、代开发票、"
    "推广链接或二维码、无上下文的营销话术。正常聊天、问候、提问、技术讨论、玩笑，"
    "以及对广告的吐槽都不要标记。只输出 JSON，格式为 "
    '{"ads":[{"id":<消息id>,"confidence":<0-100整数>,"reason":"<不超过20字的理由>"}]}；'
    '没有广告时输出 {"ads":[]}。不要输出 JSON 以外的任何内容。'
)


@dataclass(frozen=True)
class BufferedMessage:
    message_id: int
    user_id: int
    username: str
    text: str
    queued_at: float
    mentions: frozenset[str] = frozenset()
    mentioned_ids: frozenset[int] = frozenset()


@dataclass
class ChatBuffer:
    messages: list[BufferedMessage] = field(default_factory=list)
    first_at: float = 0.0
    window_sec: int = DEFAULT_WINDOW_SEC


@dataclass(frozen=True)
class AdVerdict:
    message_id: int
    confidence: int
    reason: str


def _extract_mentions(message: Any) -> tuple[frozenset[str], frozenset[int]]:
    """Collect @username handles and text-mention user ids from a message."""
    text = getattr(message, "text", "") or ""
    usernames: set[str] = set()
    user_ids: set[int] = set()
    for entity in getattr(message, "entities", None) or []:
        entity_type = getattr(entity, "type", "")
        if entity_type == "mention":
            start = int(getattr(entity, "offset", 0) or 0)
            length = int(getattr(entity, "length", 0) or 0)
            handle = text[start : start + length].strip().lstrip("@").lower()
            if handle:
                usernames.add(handle)
        elif entity_type == "text_mention":
            user = getattr(entity, "user", None)
            if user is not None:
                try:
                    user_ids.add(int(user.id))
                except (TypeError, ValueError):
                    continue
    return frozenset(usernames), frozenset(user_ids)


class AIAdGuard:
    """In-memory per-chat message buffer, flushed by the background task."""

    def __init__(self) -> None:
        self._buffers: dict[int, ChatBuffer] = {}
        # Recent @-mentions kept across windows so a bait+ad pair split by a small window is still linked.
        self._mention_memory: dict[int, list[BufferedMessage]] = {}

    def offer(self, message: Any, window_sec: int | None = DEFAULT_WINDOW_SEC) -> None:
        chat = getattr(message, "chat", None)
        user = getattr(message, "from_user", None)
        chat_id = int(getattr(chat, "id", 0) or 0)
        text = (getattr(message, "text", "") or "").strip()
        message_id = int(getattr(message, "message_id", 0) or 0)
        if chat_id == 0 or user is None or message_id <= 0 or len(text) < 2:
            return

        now = time.monotonic()
        buffer = self._buffers.get(chat_id)
        if buffer is None:
            buffer = ChatBuffer(first_at=now)
            self._buffers[chat_id] = buffer
        requested = DEFAULT_WINDOW_SEC if window_sec is None else int(window_sec)
        buffer.window_sec = min(MAX_WINDOW_SEC, max(MIN_WINDOW_SEC, requested))
        mentions, mentioned_ids = _extract_mentions(message)
        if mentions or mentioned_ids:
            self._remember_mention(
                chat_id,
                BufferedMessage(
                    message_id=message_id,
                    user_id=int(user.id),
                    username=str(getattr(user, "username", "") or ""),
                    text="",
                    queued_at=now,
                    mentions=mentions,
                    mentioned_ids=mentioned_ids,
                ),
            )
        buffer.messages.append(
            BufferedMessage(
                message_id=message_id,
                user_id=int(user.id),
                username=str(getattr(user, "username", "") or ""),
                text=text[:MAX_MESSAGE_CHARS],
                queued_at=now,
                mentions=mentions,
                mentioned_ids=mentioned_ids,
            )
        )

    def take_ready(self, now: float | None = None) -> list[tuple[int, list[BufferedMessage]]]:
        current = time.monotonic() if now is None else now
        ready: list[tuple[int, list[BufferedMessage]]] = []
        for chat_id, buffer in list(self._buffers.items()):
            if not buffer.messages:
                self._buffers.pop(chat_id, None)
                continue
            due = current - buffer.first_at >= buffer.window_sec
            if due or len(buffer.messages) >= MAX_BATCH_MESSAGES:
                ready.append((chat_id, list(buffer.messages)))
                self._buffers.pop(chat_id, None)
        return ready

    def _remember_mention(self, chat_id: int, item: BufferedMessage) -> None:
        memory = self._mention_memory.setdefault(chat_id, [])
        memory.append(item)
        cutoff = item.queued_at - MENTION_MEMORY_SEC
        memory[:] = [entry for entry in memory if entry.queued_at >= cutoff][-MENTION_MEMORY_MAX:]

    def mention_history(self, chat_id: int) -> list[BufferedMessage]:
        return list(self._mention_memory.get(chat_id, []))

    def forget_mentions(self, chat_id: int, message_ids: set[int]) -> None:
        """Drop consumed @-messages so one bait message is never punished twice."""
        if not message_ids:
            return
        memory = self._mention_memory.get(chat_id)
        if not memory:
            return
        self._mention_memory[chat_id] = [
            item for item in memory if item.message_id not in message_ids
        ]

    def pending(self) -> int:
        return sum(len(buffer.messages) for buffer in self._buffers.values())

    def clear(self, chat_id: int | None = None) -> None:
        if chat_id is None:
            self._buffers.clear()
            self._mention_memory.clear()
        else:
            self._buffers.pop(chat_id, None)
            self._mention_memory.pop(chat_id, None)


ai_ad_guard = AIAdGuard()


def build_batch_prompt(batch: list[BufferedMessage]) -> str:
    payload = [
        {
            "id": item.message_id,
            "sender": item.username or str(item.user_id),
            "text": item.text,
        }
        for item in batch
    ]
    return json.dumps(payload, ensure_ascii=False)


def _load_json_payload(raw: str) -> Any:
    text = (raw or "").strip()
    if not text:
        raise ValueError("empty response")
    text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text).strip()
    starts = [pos for pos in (text.find("{"), text.find("[")) if pos >= 0]
    if not starts:
        raise ValueError("no json")
    start = min(starts)
    try:
        value, _ = json.JSONDecoder().raw_decode(text[start:])
    except Exception as exc:  # malformed model output
        raise ValueError("bad json") from exc
    if not isinstance(value, (dict, list)):
        raise ValueError("unexpected json")
    return value


def _to_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_ad_verdicts(raw: str, valid_ids: set[int], min_confidence: int = MIN_CONFIDENCE) -> list[AdVerdict]:
    """Turn the model answer into verdicts, ignoring unknown ids and low confidence."""
    try:
        payload = _load_json_payload(raw)
    except ValueError:
        return []

    entries: list[Any] = []
    if isinstance(payload, dict):
        for key in ("ads", "items", "data", "results"):
            if isinstance(payload.get(key), list):
                entries = payload[key]
                break
        else:
            if "id" in payload or "message_id" in payload:
                entries = [payload]
    elif isinstance(payload, list):
        entries = payload

    verdicts: dict[int, AdVerdict] = {}
    for entry in entries:
        if isinstance(entry, bool):
            continue
        if isinstance(entry, int):
            message_id, confidence, reason = entry, min_confidence, ""
        elif isinstance(entry, str):
            parsed_id = _to_int(entry.strip())
            if parsed_id is None:
                continue
            message_id, confidence, reason = parsed_id, min_confidence, ""
        elif isinstance(entry, dict):
            raw_id = entry.get("id", entry.get("message_id"))
            parsed_id = _to_int(raw_id)
            if parsed_id is None:
                continue
            parsed_confidence = _to_int(entry.get("confidence", entry.get("score", min_confidence)))
            confidence = min_confidence if parsed_confidence is None else parsed_confidence
            reason = str(entry.get("reason") or "")[:MAX_REASON_CHARS]
            message_id = parsed_id
        else:
            continue

        if message_id not in valid_ids:
            continue
        confidence = max(0, min(100, confidence))
        if confidence < min_confidence:
            continue
        if message_id not in verdicts:
            verdicts[message_id] = AdVerdict(message_id=message_id, confidence=confidence, reason=reason)
    return list(verdicts.values())


def confidence_tiers(group: GroupConfig) -> list[tuple[int, str]]:
    """Return (threshold, action) pairs sorted from the highest threshold down."""
    raw_tiers = (
        (
            int(getattr(group, "ai_ad_block_high_confidence", 90) or 0),
            str(getattr(group, "ai_ad_block_high_action", "ban") or "delete"),
        ),
        (
            int(getattr(group, "ai_ad_block_mid_confidence", 75) or 0),
            str(getattr(group, "ai_ad_block_mid_action", "mute") or "delete"),
        ),
        (
            int(getattr(group, "ai_ad_block_min_confidence", 60) or 0),
            str(getattr(group, "ai_ad_block_min_action", "warn") or "delete"),
        ),
    )
    tiers: list[tuple[int, str]] = []
    for threshold, action in raw_tiers:
        normalized_action = action.strip().lower()
        if normalized_action not in VALID_AI_AD_ACTIONS:
            normalized_action = "delete"
        tiers.append((max(0, min(100, threshold)), normalized_action))
    tiers.sort(key=lambda item: item[0], reverse=True)
    return tiers


def tier_cutoff(tiers: list[tuple[int, str]]) -> int:
    return min(threshold for threshold, _ in tiers) if tiers else MIN_CONFIDENCE


def resolve_tier_action(tiers: list[tuple[int, str]], confidence: int) -> str:
    for threshold, action in tiers:
        if confidence >= threshold:
            return action
    return ""


def find_linked_mentioners(
    batch: list[BufferedMessage],
    ad_message_ids: set[int],
    history: list[BufferedMessage] | None = None,
) -> list[tuple[int, int, int, str]]:
    """Find @-driven spam choreography: someone mentions the account right before it posts an ad.

    Returns (mentioner_user_id, mentioner_message_id, ad_message_id, mentioner_username).
    history holds recent mentions from earlier windows so a small window does not split
    a bait+ad pair. Only messages earlier than the ad are considered.
    """
    ordered: list[BufferedMessage] = []
    seen_ids: set[int] = set()
    for item in list(history or []) + list(batch):
        if item.message_id in seen_ids:
            continue
        seen_ids.add(item.message_id)
        ordered.append(item)
    positions = {item.message_id: pos for pos, item in enumerate(ordered)}
    links: list[tuple[int, int, int, str]] = []
    seen: set[tuple[int, int]] = set()
    for ad_id in ad_message_ids:
        ad_pos = positions.get(ad_id)
        if ad_pos is None:
            continue
        ad_item = ordered[ad_pos]
        handle = ad_item.username.strip().lstrip("@").lower()
        if not handle and ad_item.user_id <= 0:
            continue
        for previous in ordered[:ad_pos]:
            if previous.user_id == ad_item.user_id:
                continue
            mentioned = bool(handle and handle in previous.mentions) or (
                ad_item.user_id in previous.mentioned_ids
            )
            if not mentioned:
                continue
            key = (previous.user_id, previous.message_id)
            if key in seen:
                continue
            seen.add(key)
            links.append((previous.user_id, previous.message_id, ad_id, previous.username))
    return links


def _action_config(action: str, group: GroupConfig) -> ModerationActionConfig:
    return ModerationActionConfig(
        action=action,
        kick_minutes=int(getattr(group, "ad_block_kick_minutes", 1) or 1),
        mute_minutes=int(getattr(group, "ad_block_mute_minutes", 30) or 30),
        ban_minutes=int(getattr(group, "ad_block_ban_minutes", 1440) or 1440),
    )


def _mention(user_id: int, username: str) -> str:
    return f"@{username}" if username else f"用户 {user_id}"


async def _warn_user(
    bot: Bot,
    db: AsyncSession,
    chat_id: int,
    user_id: int,
    username: str,
) -> None:
    """Delete + warn tier: increase the warning counter and remind the user in chat."""
    mention = _mention(user_id, username)
    try:
        _, total, setting = await add_warning(
            db,
            chat_id,
            user_id,
            0,
            "AI 识别为疑似广告",
        )
        await add_log(db, chat_id, user_id, username, "warned", "ai_ad_block")
    except Exception:
        logger.warning("Failed to record AI ad warning in chat %s", chat_id, exc_info=True)
        total, setting = 0, None

    limit = int(getattr(setting, "warn_limit", 0) or 0)
    if setting is not None and limit > 0 and total >= limit:
        try:
            await reset_warnings(db, chat_id, user_id)
            action = str(getattr(setting, "warn_action", "mute") or "mute")
            await apply_moderation_action(
                bot,
                db,
                chat_id,
                user_id,
                username,
                "warn_limit",
                ModerationActionConfig(
                    action=action,
                    kick_minutes=DEFAULT_KICK_MINUTES,
                    mute_minutes=setting.mute_minutes,
                    ban_minutes=setting.ban_minutes,
                ),
            )
            text = (
                f"{mention} 消息已被删除：AI 识别为疑似广告。"
                f"警告已达 {total}/{limit}，已自动执行{WARN_ACTION_LABELS.get(action, action)}。"
            )
        except Exception:
            logger.warning("Failed to apply warn limit action in chat %s", chat_id, exc_info=True)
            text = f"{mention} 消息已被删除：AI 识别为疑似广告。"
    else:
        suffix = f"警告 {total}/{limit}。" if limit > 0 else ""
        text = f"{mention} 消息已被删除：AI 识别为疑似广告。{suffix}"

    try:
        await bot.send_message(chat_id, text)
    except Exception:
        logger.warning("Failed to send AI ad warning message in chat %s", chat_id, exc_info=True)


async def handle_ai_ad_batch(
    bot: Bot,
    db: AsyncSession,
    group: GroupConfig,
    batch: list[BufferedMessage],
) -> int:
    """Ask the AI about one batch and moderate the messages it flags."""
    if not batch:
        return 0

    runtime = await get_runtime_config(db)
    if not runtime.ai_credentials.api_key:
        return 0

    tiers = confidence_tiers(group)
    valid_ids = {item.message_id for item in batch}
    try:
        raw = await deepseek_client.ask(
            build_batch_prompt(batch),
            system_prompt=AI_AD_SYSTEM_PROMPT,
            db=db,
        )
    except Exception:
        logger.warning("AI ad detection request failed for chat %s", group.chat_id, exc_info=True)
        return 0

    verdicts = parse_ad_verdicts(raw, valid_ids, min_confidence=tier_cutoff(tiers))
    if not verdicts:
        return 0

    by_id = {item.message_id: item for item in batch}
    best_actions: dict[int, tuple[str, int, str]] = {}
    verdict_actions: dict[int, str] = {}
    handled = 0

    for verdict in verdicts:
        item = by_id.get(verdict.message_id)
        if item is None:
            continue
        action = resolve_tier_action(tiers, verdict.confidence)
        if not action:
            continue
        verdict_actions[verdict.message_id] = action

        try:
            await bot.delete_message(group.chat_id, item.message_id)
        except Exception:
            pass

        previous = best_actions.get(item.user_id)
        if previous is None or ACTION_SEVERITY[action] > ACTION_SEVERITY[previous[0]]:
            best_actions[item.user_id] = (action, verdict.confidence, item.username)

        detail = f"conf={verdict.confidence};action={action}"
        if verdict.reason:
            detail = f"{detail};{verdict.reason}"
        await add_log(db, group.chat_id, item.user_id, item.username, AI_AD_EVENT, detail[:200])
        handled += 1

    # Coordinated bait: someone @-mentions the account that then posts the ad. Punish both.
    if verdict_actions and bool(getattr(group, "ai_ad_block_punish_mentioner", True)):
        linked_mentioners = find_linked_mentioners(
            batch, set(verdict_actions), history=ai_ad_guard.mention_history(group.chat_id)
        )
        ai_ad_guard.forget_mentions(
            group.chat_id, {mention_message_id for _, mention_message_id, _, _ in linked_mentioners}
        )
        for user_id, mention_message_id, ad_message_id, username in linked_mentioners:
            linked_action = verdict_actions.get(ad_message_id, "delete")
            try:
                await bot.delete_message(group.chat_id, mention_message_id)
            except Exception:
                pass
            previous = best_actions.get(user_id)
            if previous is None or ACTION_SEVERITY[linked_action] > ACTION_SEVERITY[previous[0]]:
                best_actions[user_id] = (linked_action, 0, username)
            await add_log(
                db,
                group.chat_id,
                user_id,
                username,
                AI_AD_EVENT,
                f"action={linked_action};mentioner_of={ad_message_id}"[:200],
            )
            handled += 1

    for user_id, (action, confidence, username) in best_actions.items():
        if action == "warn":
            await _warn_user(bot, db, group.chat_id, user_id, username)
            continue
        if action == "delete":
            continue
        try:
            await apply_moderation_action(
                bot,
                db,
                group.chat_id,
                user_id,
                username,
                AI_AD_EVENT,
                _action_config(action, group),
            )
        except Exception:
            logger.warning("AI ad moderation action failed in chat %s", group.chat_id, exc_info=True)

    if handled:
        logger.info("AI ad detection flagged %s message(s) in chat %s", handled, group.chat_id)
    return handled
