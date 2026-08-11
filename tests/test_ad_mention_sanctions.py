import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from aiogram.types import MessageEntity
from pydantic import ValidationError

from apps.api.app.schemas.ad_keyword import AdKeywordCreate
from apps.bot.bot_app.handlers import group_events
from apps.bot.bot_app.moderation_actions import ModerationActionConfig


CHAT_ID = -1001234567890
SENDER_ID = 10
BOT_ID = 999


def make_user(user_id: int, username: str = "", *, is_bot: bool = False):
    return SimpleNamespace(
        id=user_id,
        username=username or None,
        full_name=username or str(user_id),
        is_bot=is_bot,
    )


def make_member(
    user_id: int,
    username: str = "",
    *,
    status: str = "member",
    is_bot: bool = False,
    is_member: bool = True,
):
    return SimpleNamespace(
        status=status,
        user=make_user(user_id, username, is_bot=is_bot),
        is_member=is_member,
    )


def make_text_mention(user_id: int):
    return SimpleNamespace(type="text_mention", user=make_user(user_id))


def make_username_mention(text: str, username: str) -> MessageEntity:
    mention = f"@{username}"
    start = text.index(mention)
    offset = len(text[:start].encode("utf-16-le")) // 2
    length = len(mention.encode("utf-16-le")) // 2
    return MessageEntity(type="mention", offset=offset, length=length)


def make_message(*, text: str = "", entities=None, get_chat_member=None):
    bot = SimpleNamespace(
        id=BOT_ID,
        get_chat_member=AsyncMock(side_effect=get_chat_member),
    )
    return SimpleNamespace(
        bot=bot,
        chat=SimpleNamespace(id=CHAT_ID, title="Mention Test"),
        from_user=make_user(SENDER_ID, "sender"),
        text=text,
        entities=list(entities or []),
        delete=AsyncMock(),
    )


class SessionContext:
    def __init__(self, db):
        self.db = db

    async def __aenter__(self):
        return self.db

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class MentionTargetResolutionTests(unittest.IsolatedAsyncioTestCase):
    async def test_resolves_text_mention_directly(self):
        message = make_message(
            entities=[make_text_mention(20)],
            get_chat_member=lambda chat_id, user_id: make_member(user_id, "target"),
        )

        targets = await group_events._resolve_mentioned_sanction_targets(message, object())

        self.assertEqual(targets, [(20, "target")])
        message.bot.get_chat_member.assert_awaited_once_with(CHAT_ID, 20)

    async def test_resolves_cached_username_and_verifies_current_username(self):
        text = "promo \U0001f680 contact @Cached_User now"
        message = make_message(
            text=text,
            entities=[make_username_mention(text, "Cached_User")],
            get_chat_member=lambda chat_id, user_id: make_member(user_id, "Cached_User"),
        )

        with patch.object(
            group_events,
            "find_chat_user_ids_by_username",
            AsyncMock(return_value=[20]),
        ) as find_user_ids:
            targets = await group_events._resolve_mentioned_sanction_targets(message, object())

        self.assertEqual(targets, [(20, "Cached_User")])
        find_user_ids.assert_awaited_once_with(unittest.mock.ANY, CHAT_ID, "cached_user")
        message.bot.get_chat_member.assert_awaited_once_with(CHAT_ID, 20)

    async def test_skips_stale_cached_username(self):
        text = "contact @old_name"
        message = make_message(
            text=text,
            entities=[make_username_mention(text, "old_name")],
            get_chat_member=lambda chat_id, user_id: make_member(user_id, "new_name"),
        )

        with patch.object(
            group_events,
            "find_chat_user_ids_by_username",
            AsyncMock(return_value=[20]),
        ):
            targets = await group_events._resolve_mentioned_sanction_targets(message, object())

        self.assertEqual(targets, [])

    async def test_excludes_sender_own_bot_and_manager_but_allows_other_bot(self):
        def get_chat_member(chat_id, user_id):
            self.assertEqual(chat_id, CHAT_ID)
            if user_id == 20:
                return make_member(user_id, "admin", status="administrator")
            if user_id == 21:
                return make_member(user_id, "other_bot", is_bot=True)
            raise AssertionError(f"unexpected membership lookup for {user_id}")

        message = make_message(
            entities=[
                make_text_mention(SENDER_ID),
                make_text_mention(BOT_ID),
                make_text_mention(20),
                make_text_mention(21),
            ],
            get_chat_member=get_chat_member,
        )

        targets = await group_events._resolve_mentioned_sanction_targets(message, object())

        self.assertEqual(targets, [(21, "other_bot")])
        self.assertEqual(message.bot.get_chat_member.await_count, 2)

    async def test_skips_restricted_user_who_is_no_longer_a_member(self):
        message = make_message(
            entities=[make_text_mention(20)],
            get_chat_member=lambda chat_id, user_id: make_member(
                user_id,
                "target",
                status="restricted",
                is_member=False,
            ),
        )

        targets = await group_events._resolve_mentioned_sanction_targets(message, object())

        self.assertEqual(targets, [])

    async def test_limits_linked_targets_to_five(self):
        mentioned_ids = list(range(20, 27))
        message = make_message(
            entities=[make_text_mention(user_id) for user_id in mentioned_ids],
            get_chat_member=lambda chat_id, user_id: make_member(user_id, f"user{user_id}"),
        )

        targets = await group_events._resolve_mentioned_sanction_targets(message, object())

        self.assertEqual(
            targets,
            [(user_id, f"user{user_id}") for user_id in mentioned_ids[:5]],
        )
        self.assertEqual(message.bot.get_chat_member.await_count, 5)


class MentionSanctionExecutionTests(unittest.IsolatedAsyncioTestCase):
    async def test_one_target_failure_does_not_stop_remaining_targets(self):
        message = make_message()
        config = ModerationActionConfig(
            action="ban",
            kick_minutes=1,
            mute_minutes=30,
            ban_minutes=1440,
        )
        applied_user_ids = []

        async def apply_action(bot, db, chat_id, user_id, username, reason, action_config):
            applied_user_ids.append(user_id)
            if user_id == 20:
                raise RuntimeError("first target failed")
            self.assertEqual(chat_id, CHAT_ID)
            self.assertEqual(reason, "ad_block:test:mentioned_by:10")
            self.assertIs(action_config, config)

        with (
            patch.object(
                group_events,
                "_resolve_mentioned_sanction_targets",
                AsyncMock(return_value=[(20, "one"), (21, "two"), (22, "three")]),
            ),
            patch.object(group_events, "apply_moderation_action", side_effect=apply_action),
        ):
            await group_events._apply_mention_sanctions(
                message,
                object(),
                "ad_block:test",
                config,
            )

        self.assertEqual(applied_user_ids, [20, 21, 22])

    async def test_group_kick_action_is_propagated(self):
        message = make_message()
        config = ModerationActionConfig(
            action="kick",
            kick_minutes=2,
            mute_minutes=30,
            ban_minutes=1440,
        )

        with (
            patch.object(
                group_events,
                "_resolve_mentioned_sanction_targets",
                AsyncMock(return_value=[(20, "target")]),
            ),
            patch.object(group_events, "apply_moderation_action", AsyncMock()) as apply_action,
        ):
            await group_events._apply_mention_sanctions(message, object(), "ad_block", config)

        apply_action.assert_awaited_once_with(
            message.bot,
            unittest.mock.ANY,
            CHAT_ID,
            20,
            "target",
            "ad_block:mentioned_by:10",
            config,
        )


class GroupTextHandlerMentionTests(unittest.IsolatedAsyncioTestCase):
    async def test_ad_keyword_ban_reaches_sender_and_text_mention(self):
        db = object()
        message = make_message(
            text="promo contact",
            entities=[make_text_mention(20)],
            get_chat_member=lambda chat_id, user_id: make_member(user_id, "linked_bot", is_bot=True),
        )
        group = SimpleNamespace(ad_block_delete_message=True)
        rule = SimpleNamespace(
            keyword="promo",
            delete_message=True,
            mute_user=False,
            mute_minutes=30,
            ban_user=True,
            ban_minutes=60,
            apply_to_mentions=True,
        )
        decision = SimpleNamespace(
            blocked=True,
            reason="ad_block",
            keyword_rule=None,
            ad_keyword_rule=rule,
        )
        applied = []

        async def apply_action(bot, session, chat_id, user_id, username, reason, config):
            applied.append((user_id, reason, config.action, config.ban_minutes))

        with (
            patch.object(group_events, "SessionLocal", return_value=SessionContext(db)),
            patch.object(group_events, "get_runtime_config", AsyncMock(return_value=SimpleNamespace())),
            patch.object(group_events, "ensure_group", AsyncMock(return_value=group)),
            patch.object(group_events, "record_chat_user_identity", AsyncMock()),
            patch.object(group_events, "is_globally_banned", AsyncMock(return_value=None)),
            patch.object(group_events, "_handle_afk", AsyncMock()),
            patch.object(group_events, "_enforce_locks", AsyncMock(return_value=False)),
            patch.object(group_events, "_is_group_manager", AsyncMock(return_value=False)),
            patch.object(group_events.policy_engine, "check_message", AsyncMock(return_value=decision)),
            patch.object(group_events, "apply_moderation_action", side_effect=apply_action),
            patch.object(group_events, "add_log", AsyncMock()),
        ):
            await group_events.group_text_handler(message)

        self.assertEqual(
            applied,
            [
                (SENDER_ID, "ad_block:promo", "ban", 60),
                (20, "ad_block:promo:mentioned_by:10", "ban", 60),
            ],
        )
        message.delete.assert_awaited_once()


class AdKeywordMentionValidationTests(unittest.TestCase):
    def test_requires_member_penalty_when_linked_handling_is_enabled(self):
        with self.assertRaises(ValidationError):
            AdKeywordCreate(
                chat_id=CHAT_ID,
                keyword="promo",
                delete_message=True,
                apply_to_mentions=True,
            )

    def test_accepts_linked_handling_with_ban(self):
        payload = AdKeywordCreate(
            chat_id=CHAT_ID,
            keyword="promo",
            delete_message=True,
            ban_user=True,
            apply_to_mentions=True,
        )

        self.assertTrue(payload.apply_to_mentions)


if __name__ == "__main__":
    unittest.main()
