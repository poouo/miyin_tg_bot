import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from aiogram.methods import GetUpdates
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from apps.api.app.api.v1.community_routes import update_community_config
from apps.api.app.core import auth
from apps.api.app.models.base import Base
from apps.api.app.schemas.community import CommunityConfigUpdate
from apps.api.app.services import admin_password_service, runtime_config_service, runtime_health, update_service
from apps.api.app.services.community_feature_service import (
    add_global_ban, add_rss_subscription, get_rules, list_global_bans, list_rss_subscriptions, update_rss_last_entry,
)
from apps.api.app.services.global_ban_sync import apply_global_ban, release_global_ban
from apps.api.app.services.moderation.anti_spam import AntiSpamGuard
from apps.api.app.services.moderation.auto_recover import add_ban_sanction, list_active_ban_sanctions, mark_ban_recovered
from apps.bot.bot_app import tasks
from apps.bot.bot_app.dispatcher import build_dispatcher, track_polling
from apps.bot.bot_app.handlers.group_events import _message_lock_types


class ProjectRegressionTests(unittest.TestCase):
    def test_dispatcher_can_restart_in_same_process(self):
        self.assertIs(build_dispatcher(), build_dispatcher())

    def test_password_change_revokes_previously_signed_sessions(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "admin_password.json"
            with patch.object(admin_password_service, "_password_file", return_value=path):
                old = auth.create_admin_token()
                self.assertTrue(auth.verify_admin_token(old))
                admin_password_service.set_admin_password("a-rotated-test-password")
                self.assertFalse(auth.verify_admin_token(old))
                self.assertTrue(auth.verify_admin_token(auth.create_admin_token()))

    def test_login_uses_server_resolved_peer_address(self):
        request = SimpleNamespace(client=SimpleNamespace(host="192.0.2.15"), headers={"x-forwarded-for": "192.0.2.25"})
        self.assertEqual(auth.get_client_ip(request), "192.0.2.15")

    def test_alternating_text_hits_same_text_threshold_and_global_limit(self):
        guard = AntiSpamGuard()
        outcomes = [guard.hit(-100, 123, text, 30, 3, 6) for text in ["A", "B", "A", "B", "A"]]
        self.assertEqual(outcomes, [False, False, False, False, True])
        outcomes = [
            guard.hit(-100, 124, str(i), 30, 10, 10, global_window_sec=30, global_max_messages=3)
            for i in range(3)
        ]
        self.assertEqual(outcomes, [False, False, True])

    def test_media_with_forward_and_link_matches_all_locks(self):
        message = SimpleNamespace(
            text=None, caption="https://example.invalid", entities=[], caption_entities=[],
            photo=[object()], forward_origin=object(),
        )
        self.assertEqual(_message_lock_types(message), {"media", "links", "forwards"})

    def test_docker_image_update_checks_registry_revision(self):
        env = {"MIYIN_DOCKER_SOURCE": "image", "MIYIN_BUILD_REVISION": "1" * 40}
        with (
            patch.object(update_service.os, "getenv", side_effect=lambda key, default=None: env.get(key, default)),
            patch.object(update_service, "_latest_image_revision", return_value="1" * 40) as image,
            patch.object(update_service, "_run") as git,
        ):
            result = update_service._check_docker_update(Path("."), "V1.0.05")
        self.assertEqual((result["compare_mode"], result["has_update"]), ("image", False))
        image.assert_called_once()
        git.assert_not_called()


class DatabaseRegressionTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        self.addAsyncCleanup(engine.dispose)
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        self.sessions = async_sessionmaker(engine, expire_on_commit=False)
        cache = patch.object(runtime_config_service, "_runtime_cache", None)
        cache_time = patch.object(runtime_config_service, "_runtime_cache_at", 0.0)
        cache.start()
        cache_time.start()
        self.addCleanup(cache.stop)
        self.addCleanup(cache_time.stop)

    async def test_bad_log_channel_rolls_back_other_community_settings(self):
        async with self.sessions() as db:
            with self.assertRaises(HTTPException) as exc:
                await update_community_config(100, CommunityConfigUpdate(rules_text="new rules", log_enabled=True), db)
            self.assertEqual(exc.exception.status_code, 400)
        async with self.sessions() as db:
            self.assertIsNone(await get_rules(db, 100))
        async with self.sessions() as db:
            config = await update_community_config(100, CommunityConfigUpdate(rules_text="saved"), db)
            self.assertEqual(config.rules_text, "saved")

    async def test_runtime_initializes_from_environment_once(self):
        env_settings = Mock(telegram_admin_ids_raw="123")
        env_settings.model_dump.return_value = {"telegram_bot_token": "123:configured-in-env"}
        with patch.object(runtime_config_service, "settings", env_settings):
            async with self.sessions() as db:
                runtime = await runtime_config_service.get_runtime_config(db)
                self.assertEqual(runtime.telegram_bot_token, "123:configured-in-env")
                await runtime_config_service.update_runtime_config(db, {"telegram_bot_token": ""})
                self.assertEqual((await runtime_config_service.get_runtime_config(db)).telegram_bot_token, "")

    async def test_duplicate_ban_rows_are_deduped_and_cleared_together(self):
        async with self.sessions() as db:
            await add_ban_sanction(db, -100, 123, "first", 60)
            await add_ban_sanction(db, -100, 123, "second", 60)
            self.assertEqual(len(await list_active_ban_sanctions(db)), 1)
            await mark_ban_recovered(db, -100, 123)
            self.assertEqual(await list_active_ban_sanctions(db), [])

    async def test_bot_health_requires_a_successful_poll(self):
        with patch.object(runtime_health, "_bot", {"state": "starting", "last_success": None}):
            self.assertEqual(runtime_health.bot_health()["state"], "starting")
            await track_polling(AsyncMock(return_value=[]), None, GetUpdates())
            self.assertEqual(runtime_health.bot_health()["state"], "online")
            old_poll = runtime_health.bot_health()["last_success"]
            with self.assertRaises(RuntimeError):
                await track_polling(AsyncMock(side_effect=RuntimeError("offline")), None, GetUpdates())
            self.assertEqual(runtime_health.bot_health(), {"state": "error", "last_success": old_poll})

    async def test_rss_retains_failed_entry_and_publishes_all_new_entries_in_order(self):
        xml = """<rss><channel><title>Feed</title>
        <item><guid>1</guid><title>Old</title><pubDate>Mon, 23 Nov 2026 10:00:00 GMT</pubDate></item>
        <item><guid>2</guid><title>A &amp; B</title><pubDate>Tue, 24 Nov 2026 10:00:00 GMT</pubDate></item>
        <item><guid>3</guid><title>C</title><pubDate>Wed, 25 Nov 2026 10:00:00 GMT</pubDate></item>
        </channel></rss>"""
        title, entries = tasks._parse_feed_items(xml)
        bot = SimpleNamespace(send_message=AsyncMock(side_effect=[None, RuntimeError("offline"), None]))
        async with self.sessions() as db:
            sub = await add_rss_subscription(db, -100, "https://example.invalid/rss")
            await update_rss_last_entry(db, sub.id, "1")
        with patch.object(tasks, "SessionLocal", self.sessions):
            await tasks._deliver_rss_items(bot, sub, title, entries)
            async with self.sessions() as db:
                sub = (await list_rss_subscriptions(db, -100))[0]
                self.assertEqual(sub.last_entry_id, "2")
            await tasks._deliver_rss_items(bot, sub, title, entries)
        async with self.sessions() as db:
            sub = (await list_rss_subscriptions(db, -100))[0]
            self.assertEqual(sub.last_entry_id, "3")
        self.assertEqual([call.args[1] for call in bot.send_message.await_args_list], ["<b>A &amp; B</b>", "<b>C</b>", "<b>C</b>"])

    async def test_global_release_retries_failed_group_without_releasing_local_ban(self):
        bot = SimpleNamespace(ban_chat_member=AsyncMock(), unban_chat_member=AsyncMock(side_effect=RuntimeError("offline")))
        async with self.sessions() as db:
            await add_global_ban(db, 123, 1)
            await add_ban_sanction(db, -101, 123, "manual_ban", 60)
            await apply_global_ban(bot, db, -101, 123)
            await apply_global_ban(bot, db, -100, 123)
            result = await release_global_ban(bot, db, 123)
            self.assertEqual(result["failed"], [-100])
            self.assertFalse((await list_global_bans(db))[0].active)
            self.assertEqual(bot.ban_chat_member.await_args.args, (-101, 123))
            self.assertIn("until_date", bot.ban_chat_member.await_args.kwargs)
            bot.unban_chat_member.side_effect = None
            self.assertEqual((await release_global_ban(bot, db, 123))["failed"], [])
            self.assertEqual(await list_global_bans(db), [])
            self.assertEqual([item.chat_id for item in await list_active_ban_sanctions(db)], [-101])
