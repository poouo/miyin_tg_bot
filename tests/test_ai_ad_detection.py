import json
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import apps.api.app.models.entities  # noqa: F401  (registers tables on Base)
from apps.api.app.models.base import Base
from apps.api.app.models.entities import ModerationLog, UserSanction, UserWarning
from apps.api.app.services import runtime_config_service as config_service
from apps.api.app.services.community_feature_service import update_warning_setting
from apps.api.app.services.group_service import ensure_group
from apps.bot.bot_app.ai_ad_guard import (
    AI_AD_EVENT,
    MAX_BATCH_MESSAGES,
    MAX_WINDOW_SEC,
    MENTION_MEMORY_MAX,
    MIN_CONFIDENCE,
    MIN_WINDOW_SEC,
    AdVerdict,
    AIAdGuard,
    ai_ad_guard,
    BufferedMessage,
    build_batch_prompt,
    confidence_tiers,
    find_linked_mentioners,
    handle_ai_ad_batch,
    parse_ad_verdicts,
    resolve_tier_action,
    tier_cutoff,
)
from apps.bot.bot_app.state import deepseek_client

CHAT_ID = -1001234567890
SPAMMER_ID = 7001
MEMBER_ID = 7002


def _message(message_id, text, user_id=SPAMMER_ID, username="spammer", chat_id=CHAT_ID, entities=None):
    return SimpleNamespace(
        chat=SimpleNamespace(id=chat_id),
        message_id=message_id,
        text=text,
        from_user=SimpleNamespace(id=user_id, username=username),
        entities=entities or [],
    )


def _buffered(message_id, text, user_id=SPAMMER_ID, username="spammer", mentions=frozenset(), mentioned_ids=frozenset()):
    return BufferedMessage(
        message_id=message_id,
        user_id=user_id,
        username=username,
        text=text,
        queued_at=0.0,
        mentions=mentions,
        mentioned_ids=mentioned_ids,
    )


def _group(**overrides):
    settings = {
        "ai_ad_block_high_confidence": 90,
        "ai_ad_block_high_action": "ban",
        "ai_ad_block_mid_confidence": 75,
        "ai_ad_block_mid_action": "mute",
        "ai_ad_block_min_confidence": 60,
        "ai_ad_block_min_action": "warn",
        "ad_block_kick_minutes": 1,
        "ad_block_mute_minutes": 30,
        "ad_block_ban_minutes": 1440,
    }
    settings.update(overrides)
    return SimpleNamespace(**settings)


class ParseAdVerdictTests(unittest.TestCase):
    def test_standard_answer(self):
        raw = json.dumps({"ads": [{"id": 11, "confidence": 90, "reason": "推销"}]})
        verdicts = parse_ad_verdicts(raw, {11, 12})
        self.assertEqual(verdicts, [AdVerdict(11, 90, "推销")])

    def test_code_fenced_answer(self):
        fence = chr(96) * 3
        raw = fence + 'json\n{"ads":[{"id":11,"confidence":88}]}\n' + fence
        self.assertEqual([item.message_id for item in parse_ad_verdicts(raw, {11})], [11])

    def test_plain_id_list(self):
        self.assertEqual(
            [item.message_id for item in parse_ad_verdicts("[11, 12]", {11, 12, 13})],
            [11, 12],
        )

    def test_message_id_key_and_text_prefix(self):
        raw = '这里是结果：{"ads":[{"message_id":12,"score":80,"reason":"引流"}]}'
        verdicts = parse_ad_verdicts(raw, {12})
        self.assertEqual(verdicts[0].message_id, 12)
        self.assertEqual(verdicts[0].confidence, 80)

    def test_custom_min_confidence(self):
        raw = json.dumps({"ads": [{"id": 11, "confidence": 70}]})
        self.assertEqual(parse_ad_verdicts(raw, {11}, min_confidence=80), [])
        self.assertEqual(len(parse_ad_verdicts(raw, {11}, min_confidence=60)), 1)

    def test_unknown_ids_are_ignored(self):
        raw = json.dumps({"ads": [{"id": 999, "confidence": 99}]})
        self.assertEqual(parse_ad_verdicts(raw, {11}), [])

    def test_duplicate_ids_keep_first(self):
        raw = json.dumps({"ads": [{"id": 11, "confidence": 90, "reason": "a"}, {"id": 11, "confidence": 70, "reason": "b"}]})
        verdicts = parse_ad_verdicts(raw, {11})
        self.assertEqual(len(verdicts), 1)
        self.assertEqual(verdicts[0].confidence, 90)

    def test_non_json_and_wrong_shapes(self):
        for raw in ("", "抱歉，我无法判断", "[]", "null", "42", '"text"'):
            self.assertEqual(parse_ad_verdicts(raw, {11}), [], raw)

    def test_missing_confidence_defaults_to_threshold(self):
        raw = json.dumps({"ads": [{"id": 11}]})
        self.assertEqual(parse_ad_verdicts(raw, {11})[0].confidence, MIN_CONFIDENCE)


class BuildBatchPromptTests(unittest.TestCase):
    def test_prompt_is_json_with_ids_and_senders(self):
        prompt = build_batch_prompt([
            _buffered(11, "加我微信 返利", user_id=SPAMMER_ID, username="spammer"),
            _buffered(12, "早上好", user_id=MEMBER_ID, username="member"),
        ])
        payload = json.loads(prompt)
        self.assertEqual([item["id"] for item in payload], [11, 12])
        self.assertEqual(payload[0]["sender"], "spammer")
        self.assertEqual(payload[1]["text"], "早上好")


class TierResolutionTests(unittest.TestCase):
    def test_tiers_sorted_descending(self):
        tiers = confidence_tiers(_group())
        self.assertEqual(tiers, [(90, "ban"), (75, "mute"), (60, "warn")])
        self.assertEqual(tier_cutoff(tiers), 60)

    def test_bad_action_falls_back_to_delete(self):
        tiers = confidence_tiers(_group(ai_ad_block_high_action="nuke"))
        self.assertEqual(tiers[0], (90, "delete"))

    def test_inverted_thresholds_are_still_ordered(self):
        tiers = confidence_tiers(
            _group(
                ai_ad_block_high_confidence=50,
                ai_ad_block_high_action="ban",
                ai_ad_block_mid_confidence=95,
                ai_ad_block_mid_action="mute",
            )
        )
        self.assertEqual(tiers[0], (95, "mute"))
        self.assertEqual(tier_cutoff(tiers), 50)

    def test_resolve_tier_action_boundaries(self):
        tiers = confidence_tiers(_group())
        self.assertEqual(resolve_tier_action(tiers, 100), "ban")
        self.assertEqual(resolve_tier_action(tiers, 90), "ban")
        self.assertEqual(resolve_tier_action(tiers, 89), "mute")
        self.assertEqual(resolve_tier_action(tiers, 75), "mute")
        self.assertEqual(resolve_tier_action(tiers, 74), "warn")
        self.assertEqual(resolve_tier_action(tiers, 60), "warn")
        self.assertEqual(resolve_tier_action(tiers, 59), "")


class MentionExtractionTests(unittest.TestCase):
    def test_username_mention_entity_is_captured(self):
        guard = AIAdGuard()
        text = "@Spammer 快来看"
        entities = [SimpleNamespace(type="mention", offset=0, length=len("@Spammer"))]
        guard.offer(_message(11, text, user_id=8001, username="bait", entities=entities), window_sec=30)
        item = guard._buffers[CHAT_ID].messages[0]
        self.assertEqual(item.mentions, frozenset({"spammer"}))
        self.assertEqual(item.mentioned_ids, frozenset())

    def test_text_mention_entity_captures_user_id(self):
        guard = AIAdGuard()
        entities = [SimpleNamespace(type="text_mention", offset=0, length=4, user=SimpleNamespace(id=SPAMMER_ID))]
        guard.offer(_message(11, "你好", user_id=8001, username="bait", entities=entities), window_sec=30)
        item = guard._buffers[CHAT_ID].messages[0]
        self.assertEqual(item.mentioned_ids, frozenset({SPAMMER_ID}))


class MentionLinkingTests(unittest.TestCase):
    def test_link_when_mention_precedes_flagged_ad(self):
        batch = [
            _buffered(10, "@spammer 快来看", user_id=8001, username="bait", mentions=frozenset({"spammer"})),
            _buffered(11, "进群领福利 日赚500"),
        ]
        links = find_linked_mentioners(batch, {11})
        self.assertEqual(links, [(8001, 10, 11, "bait")])

    def test_link_via_text_mention_user_id(self):
        batch = [
            _buffered(10, "快来看", user_id=8001, username="bait", mentioned_ids=frozenset({SPAMMER_ID})),
            _buffered(11, "广告内容"),
        ]
        self.assertEqual(find_linked_mentioners(batch, {11}), [(8001, 10, 11, "bait")])

    def test_mention_after_the_ad_is_not_linked(self):
        batch = [
            _buffered(11, "广告内容"),
            _buffered(12, "@spammer 收到", user_id=8001, username="bait", mentions=frozenset({"spammer"})),
        ]
        self.assertEqual(find_linked_mentioners(batch, {11}), [])

    def test_mentioning_someone_else_is_not_linked(self):
        batch = [
            _buffered(10, "@someoneelse 你好", user_id=8001, username="bait", mentions=frozenset({"someoneelse"})),
            _buffered(11, "广告内容"),
        ]
        self.assertEqual(find_linked_mentioners(batch, {11}), [])

    def test_history_mention_links_across_split_windows(self):
        history = [
            _buffered(20, "@spammer 快来看", user_id=8001, username="bait", mentions=frozenset({"spammer"})),
        ]
        batch = [_buffered(21, "广告内容")]
        self.assertEqual(find_linked_mentioners(batch, {21}, history=history), [(8001, 20, 21, "bait")])

    def test_history_and_batch_duplicate_is_counted_once(self):
        mention = _buffered(20, "@spammer 快来看", user_id=8001, username="bait", mentions=frozenset({"spammer"}))
        batch = [mention, _buffered(21, "广告内容")]
        self.assertEqual(find_linked_mentioners(batch, {21}, history=[mention]), [(8001, 20, 21, "bait")])

    def test_self_mention_is_ignored(self):
        batch = [
            _buffered(10, "@spammer 我来了", mentions=frozenset({"spammer"})),
            _buffered(11, "广告内容"),
        ]
        self.assertEqual(find_linked_mentioners(batch, {11}), [])


class AIAdGuardTests(unittest.TestCase):
    def test_offer_and_window(self):
        guard = AIAdGuard()
        guard.offer(_message(11, "加我微信返利"), window_sec=30)
        start = time.monotonic()
        self.assertEqual(guard.take_ready(now=start + 5), [])
        ready = guard.take_ready(now=start + 31)
        self.assertEqual(len(ready), 1)
        chat_id, batch = ready[0]
        self.assertEqual(chat_id, CHAT_ID)
        self.assertEqual([item.message_id for item in batch], [11])

    def test_window_is_clamped_to_one_and_sixty_seconds(self):
        guard = AIAdGuard()
        guard.offer(_message(11, "广告"), window_sec=0)
        self.assertEqual(guard._buffers[CHAT_ID].window_sec, MIN_WINDOW_SEC)
        guard.clear()
        guard.offer(_message(12, "广告"), window_sec=999)
        self.assertEqual(guard._buffers[CHAT_ID].window_sec, MAX_WINDOW_SEC)

    def test_one_second_window_is_ready_after_one_second(self):
        guard = AIAdGuard()
        guard.offer(_message(11, "广告"), window_sec=1)
        self.assertEqual(guard.take_ready(now=time.monotonic() + 0.5), [])
        self.assertEqual(len(guard.take_ready(now=time.monotonic() + 2)), 1)

    def test_short_or_invalid_messages_are_skipped(self):
        guard = AIAdGuard()
        guard.offer(_message(11, " "), window_sec=30)
        guard.offer(_message(0, "广告广告"), window_sec=30)
        guard.offer(
            SimpleNamespace(chat=SimpleNamespace(id=CHAT_ID), message_id=12, text="广告广告", from_user=None),
            window_sec=30,
        )
        self.assertEqual(guard.take_ready(now=time.monotonic() + 999), [])

    def test_full_batch_is_ready_before_window_ends(self):
        guard = AIAdGuard()
        for index in range(MAX_BATCH_MESSAGES):
            guard.offer(_message(index + 1, "广告内容"), window_sec=60)
        ready = guard.take_ready(now=time.monotonic() + 1)
        self.assertEqual(len(ready), 1)
        self.assertEqual(len(ready[0][1]), MAX_BATCH_MESSAGES)

    def test_mention_memory_is_bounded_and_cleared(self):
        guard = AIAdGuard()
        for index in range(MENTION_MEMORY_MAX + 10):
            text = "@spammer hi"
            entities = [SimpleNamespace(type="mention", offset=0, length=len("@spammer"))]
            guard.offer(_message(index + 1, text, user_id=8001, username="bait", entities=entities), window_sec=30)
        self.assertEqual(len(guard.mention_history(CHAT_ID)), MENTION_MEMORY_MAX)
        guard.clear(CHAT_ID)
        self.assertEqual(guard.mention_history(CHAT_ID), [])

    def test_messages_without_mentions_are_not_remembered(self):
        guard = AIAdGuard()
        guard.offer(_message(11, "普通聊天"), window_sec=30)
        self.assertEqual(guard.mention_history(CHAT_ID), [])

    def test_forget_mentions_removes_consumed_entries(self):
        guard = AIAdGuard()
        entities = [SimpleNamespace(type="mention", offset=0, length=len("@spammer"))]
        guard.offer(_message(11, "@spammer hi", user_id=8001, entities=entities), window_sec=30)
        guard.offer(_message(12, "@spammer hi2", user_id=8001, entities=entities), window_sec=30)
        guard.forget_mentions(CHAT_ID, {11})
        self.assertEqual([item.message_id for item in guard.mention_history(CHAT_ID)], [12])

    def test_buffers_are_per_chat_and_clearable(self):
        guard = AIAdGuard()
        guard.offer(_message(11, "广告一"), window_sec=30)
        guard.offer(_message(21, "广告二", chat_id=-100999), window_sec=30)
        self.assertEqual(guard.pending(), 2)
        guard.clear(CHAT_ID)
        self.assertEqual(guard.pending(), 1)
        guard.clear()
        self.assertEqual(guard.pending(), 0)


class _FakeBot:
    def __init__(self):
        self.deleted = []
        self.restricted = []
        self.banned = []
        self.messages = []

    async def delete_message(self, chat_id, message_id):
        self.deleted.append((chat_id, message_id))

    async def restrict_chat_member(self, chat_id, user_id, permissions=None, until_date=None):
        self.restricted.append((chat_id, user_id, until_date))

    async def ban_chat_member(self, chat_id, user_id, until_date=None):
        self.banned.append((chat_id, user_id))

    async def send_message(self, chat_id, text, **kwargs):
        self.messages.append((chat_id, text))


class HandleBatchTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="miyin ai ad test ")
        self.addCleanup(self._tmp.cleanup)
        db_path = Path(self._tmp.name) / "test.db"
        self.engine = create_async_engine(f"sqlite+aiosqlite:///{db_path.as_posix()}")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.sessions = async_sessionmaker(self.engine, expire_on_commit=False)
        self.addAsyncCleanup(self.engine.dispose)
        self.client_patch = patch.object(deepseek_client, "ask", AsyncMock(return_value='{"ads":[]}'))
        self.ask_mock = self.client_patch.start()
        self.addCleanup(self.client_patch.stop)
        ai_ad_guard.clear()

    async def asyncTearDown(self):
        config_service._runtime_cache = None
        config_service._runtime_cache_at = 0.0

    async def _prepare(self, *, api_key="sk-test", high=90, high_action="ban", mid=75, mid_action="mute", min_confidence=60, min_action="warn"):
        async with self.sessions() as db:
            await config_service.update_runtime_config(db, {"deepseek_api_key": api_key})
            group = await ensure_group(db, CHAT_ID, "test group")
            group.ai_ad_block_enabled = True
            group.ai_ad_block_high_confidence = high
            group.ai_ad_block_high_action = high_action
            group.ai_ad_block_mid_confidence = mid
            group.ai_ad_block_mid_action = mid_action
            group.ai_ad_block_min_confidence = min_confidence
            group.ai_ad_block_min_action = min_action
            await db.commit()
            return group

    async def test_high_confidence_is_banned(self):
        group = await self._prepare()
        self.ask_mock.return_value = json.dumps({"ads": [{"id": 11, "confidence": 95, "reason": "引流"}]})
        bot = _FakeBot()
        batch = [_buffered(11, "加我微信返利"), _buffered(12, "早上好", user_id=MEMBER_ID, username="member")]

        async with self.sessions() as db:
            handled = await handle_ai_ad_batch(bot, db, group, batch)

            self.assertEqual(handled, 1)
            self.assertEqual(bot.deleted, [(CHAT_ID, 11)])
            self.assertEqual(len(bot.banned), 1)
            self.assertEqual(bot.banned[0][:2], (CHAT_ID, SPAMMER_ID))
            self.assertEqual(bot.restricted, [])
            log_types = {row.event_type for row in (await db.execute(select(ModerationLog))).scalars().all()}
            self.assertIn(AI_AD_EVENT, log_types)
            self.assertIn("user_banned", log_types)
            details = [row.detail for row in (await db.execute(select(ModerationLog).where(ModerationLog.event_type == AI_AD_EVENT))).scalars().all()]
            self.assertTrue(any("conf=95" in detail and "action=ban" in detail for detail in details), details)

    async def test_mid_confidence_is_muted(self):
        group = await self._prepare()
        self.ask_mock.return_value = json.dumps({"ads": [{"id": 11, "confidence": 80}]})
        bot = _FakeBot()
        async with self.sessions() as db:
            handled = await handle_ai_ad_batch(bot, db, group, [_buffered(11, "进群领福利")])
            self.assertEqual(handled, 1)
            self.assertEqual(len(bot.restricted), 1)
            self.assertEqual(bot.banned, [])
            self.assertEqual(bot.messages, [])

    async def test_min_confidence_warns_in_chat(self):
        group = await self._prepare()
        self.ask_mock.return_value = json.dumps({"ads": [{"id": 11, "confidence": 65}]})
        bot = _FakeBot()
        async with self.sessions() as db:
            handled = await handle_ai_ad_batch(bot, db, group, [_buffered(11, "看看这个", username="spammer")])
            self.assertEqual(handled, 1)
            self.assertEqual(bot.deleted, [(CHAT_ID, 11)])
            self.assertEqual(bot.restricted, [])
            self.assertEqual(len(bot.messages), 1)
            self.assertIn("AI 识别为疑似广告", bot.messages[0][1])
            self.assertNotIn("置信度", bot.messages[0][1])
            warnings = (await db.execute(select(UserWarning))).scalars().all()
            self.assertEqual(len(warnings), 1)

    async def test_warn_tier_reaches_warn_limit(self):
        group = await self._prepare()
        async with self.sessions() as db:
            await update_warning_setting(db, CHAT_ID, warn_limit=1)
        self.ask_mock.return_value = json.dumps({"ads": [{"id": 11, "confidence": 65}]})
        bot = _FakeBot()
        async with self.sessions() as db:
            await handle_ai_ad_batch(bot, db, group, [_buffered(11, "广告")])
            self.assertEqual(len(bot.restricted), 1)
            self.assertIn("警告已达", bot.messages[-1][1])
            self.assertNotIn("置信度", bot.messages[-1][1])
            active_warnings = (
                await db.execute(select(UserWarning).where(UserWarning.active.is_(True)))
            ).scalars().all()
            self.assertEqual(active_warnings, [])

    async def test_delete_tier_only_deletes(self):
        group = await self._prepare(min_action="delete")
        self.ask_mock.return_value = json.dumps({"ads": [{"id": 11, "confidence": 65}]})
        bot = _FakeBot()
        async with self.sessions() as db:
            self.assertEqual(await handle_ai_ad_batch(bot, db, group, [_buffered(11, "广告")]), 1)
        self.assertEqual(bot.deleted, [(CHAT_ID, 11)])
        self.assertEqual(bot.restricted, [])
        self.assertEqual(bot.banned, [])
        self.assertEqual(bot.messages, [])

    async def test_below_cutoff_is_ignored(self):
        group = await self._prepare(min_confidence=80)
        self.ask_mock.return_value = json.dumps({"ads": [{"id": 11, "confidence": 70}]})
        bot = _FakeBot()
        async with self.sessions() as db:
            self.assertEqual(await handle_ai_ad_batch(bot, db, group, [_buffered(11, "广告")]), 0)
        self.assertEqual(bot.deleted, [])

    async def test_same_user_gets_strongest_action_once(self):
        group = await self._prepare()
        self.ask_mock.return_value = json.dumps(
            {"ads": [{"id": 11, "confidence": 95}, {"id": 12, "confidence": 80}]}
        )
        bot = _FakeBot()
        batch = [_buffered(11, "广告一"), _buffered(12, "广告二")]
        async with self.sessions() as db:
            handled = await handle_ai_ad_batch(bot, db, group, batch)
            self.assertEqual(handled, 2)
            self.assertEqual(len(bot.deleted), 2)
            self.assertEqual(len(bot.banned), 1)
            self.assertEqual(bot.restricted, [])

    async def test_linked_mentioner_is_deleted_and_punished(self):
        group = await self._prepare()
        self.ask_mock.return_value = json.dumps({"ads": [{"id": 11, "confidence": 95}]})
        bot = _FakeBot()
        batch = [
            _buffered(10, "@spammer 快来看", user_id=8001, username="bait", mentions=frozenset({"spammer"})),
            _buffered(11, "加我微信 返利 日赚500"),
        ]
        async with self.sessions() as db:
            handled = await handle_ai_ad_batch(bot, db, group, batch)
            self.assertEqual(handled, 2)
            self.assertEqual(sorted(bot.deleted), [(CHAT_ID, 10), (CHAT_ID, 11)])
            self.assertEqual({item[1] for item in bot.banned}, {SPAMMER_ID, 8001})
            details = [
                row.detail
                for row in (
                    await db.execute(select(ModerationLog).where(ModerationLog.event_type == AI_AD_EVENT))
                ).scalars().all()
            ]
            self.assertTrue(any("mentioner_of=11" in detail for detail in details), details)

    async def test_mention_from_previous_window_is_linked(self):
        group = await self._prepare()
        entities = [SimpleNamespace(type="mention", offset=0, length=len("@spammer"))]
        ai_ad_guard.offer(
            _message(20, "@spammer 快来看", user_id=8001, username="bait", entities=entities),
            window_sec=5,
        )
        ai_ad_guard._buffers.clear()  # simulate the mention being flushed in an earlier window
        self.ask_mock.return_value = json.dumps({"ads": [{"id": 21, "confidence": 95}]})
        bot = _FakeBot()
        async with self.sessions() as db:
            handled = await handle_ai_ad_batch(bot, db, group, [_buffered(21, "广告内容")])
            self.assertEqual(handled, 2)
            self.assertEqual(sorted(bot.deleted), [(CHAT_ID, 20), (CHAT_ID, 21)])
            self.assertEqual({item[1] for item in bot.banned}, {SPAMMER_ID, 8001})

    async def test_linked_mention_is_not_reused_for_later_ads(self):
        group = await self._prepare()
        entities = [SimpleNamespace(type="mention", offset=0, length=len("@spammer"))]
        ai_ad_guard.offer(
            _message(20, "@spammer 快来看", user_id=8001, username="bait", entities=entities),
            window_sec=30,
        )
        self.ask_mock.return_value = json.dumps({"ads": [{"id": 21, "confidence": 95}]})
        bot_first = _FakeBot()
        async with self.sessions() as db:
            await handle_ai_ad_batch(
                bot_first,
                db,
                group,
                [
                    _buffered(20, "@spammer 快来看", user_id=8001, username="bait", mentions=frozenset({"spammer"})),
                    _buffered(21, "广告内容"),
                ],
            )
        self.assertEqual(ai_ad_guard.mention_history(CHAT_ID), [])

        self.ask_mock.return_value = json.dumps({"ads": [{"id": 31, "confidence": 95}]})
        bot_second = _FakeBot()
        async with self.sessions() as db:
            handled = await handle_ai_ad_batch(bot_second, db, group, [_buffered(31, "又一条广告")])
            self.assertEqual(handled, 1)
            self.assertEqual({item[1] for item in bot_second.banned}, {SPAMMER_ID})

    async def test_mentioner_link_can_be_disabled(self):
        group = await self._prepare()
        group.ai_ad_block_punish_mentioner = False
        self.ask_mock.return_value = json.dumps({"ads": [{"id": 11, "confidence": 95}]})
        bot = _FakeBot()
        batch = [
            _buffered(10, "@spammer 快来看", user_id=8001, username="bait", mentions=frozenset({"spammer"})),
            _buffered(11, "广告内容"),
        ]
        async with self.sessions() as db:
            handled = await handle_ai_ad_batch(bot, db, group, batch)
            self.assertEqual(handled, 1)
            self.assertEqual(bot.deleted, [(CHAT_ID, 11)])
            self.assertEqual({item[1] for item in bot.banned}, {SPAMMER_ID})

    async def test_innocent_mention_is_not_punished(self):
        group = await self._prepare()
        self.ask_mock.return_value = json.dumps({"ads": [{"id": 11, "confidence": 95}]})
        bot = _FakeBot()
        batch = [
            _buffered(10, "@someoneelse 你好", user_id=8001, username="bait", mentions=frozenset({"someoneelse"})),
            _buffered(11, "广告内容"),
        ]
        async with self.sessions() as db:
            handled = await handle_ai_ad_batch(bot, db, group, batch)
            self.assertEqual(handled, 1)
            self.assertEqual(bot.deleted, [(CHAT_ID, 11)])
            self.assertEqual({item[1] for item in bot.banned}, {SPAMMER_ID})

    async def test_missing_api_key_skips_ai_call(self):
        group = await self._prepare(api_key="")
        bot = _FakeBot()
        async with self.sessions() as db:
            self.assertEqual(await handle_ai_ad_batch(bot, db, group, [_buffered(11, "广告")]), 0)
        self.assertEqual(self.ask_mock.await_count, 0)
        self.assertEqual(bot.deleted, [])

    async def test_ai_error_is_swallowed(self):
        group = await self._prepare()
        self.ask_mock.side_effect = RuntimeError("network down")
        bot = _FakeBot()
        async with self.sessions() as db:
            self.assertEqual(await handle_ai_ad_batch(bot, db, group, [_buffered(11, "广告")]), 0)
        self.assertEqual(bot.deleted, [])


if __name__ == "__main__":
    unittest.main()
