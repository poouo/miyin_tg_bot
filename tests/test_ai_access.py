import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import httpx
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import apps.api.app.models.entities  # noqa: F401  (registers tables on Base)
from apps.api.app.api.v1.group_routes import router as group_router
from apps.api.app.core.db import get_db
from apps.api.app.models.base import Base
from apps.api.app.services.group_service import ensure_group, get_group
from apps.api.app.services.runtime_config_service import RuntimeConfig
from apps.bot.bot_app.ai_access import (
    AI_ADMIN_ONLY,
    AI_ALLOWED,
    AI_DISABLED,
    AI_PRIVATE_DENIED,
    check_ai_access,
)

CHAT_ID = -1001234567890
BOT_ADMIN_ID = 111
GROUP_ADMIN_ID = 222
CREATOR_ID = 233
MEMBER_ID = 333


def _runtime(admin_ids: str = str(BOT_ADMIN_ID)) -> RuntimeConfig:
    return RuntimeConfig(
        telegram_bot_token="",
        telegram_bot_username="bot",
        telegram_admin_ids=admin_ids,
        deepseek_api_key="k",
        deepseek_base_url="https://example.invalid",
        deepseek_model="m",
        deepseek_timeout_sec=30,
        join_verify_timeout_sec=180,
        spam_window_sec=10,
        spam_max_messages=5,
        ad_regex="",
    )


class _FakeBot:
    def __init__(self, statuses=None, fail=False):
        self.statuses = statuses or {GROUP_ADMIN_ID: "administrator", CREATOR_ID: "creator", MEMBER_ID: "member"}
        self.fail = fail
        self.calls = 0

    async def get_chat_member(self, chat_id, user_id):
        self.calls += 1
        if self.fail:
            raise RuntimeError("telegram unavailable")
        return SimpleNamespace(status=self.statuses.get(user_id, "left"))


def _message(user_id, *, chat_type="supergroup", sender_chat_id=None, bot=None):
    return SimpleNamespace(
        chat=SimpleNamespace(id=CHAT_ID, type=chat_type),
        from_user=SimpleNamespace(id=user_id) if user_id is not None else None,
        sender_chat=SimpleNamespace(id=sender_chat_id) if sender_chat_id is not None else None,
        bot=bot or _FakeBot(),
    )


def _group(*, ai=True, members=True):
    return SimpleNamespace(deepseek_enabled=ai, ai_member_enabled=members)


class CheckAiAccessTests(unittest.IsolatedAsyncioTestCase):
    async def test_members_allowed_when_member_switch_is_on(self):
        bot = _FakeBot()
        result = await check_ai_access(_message(MEMBER_ID, bot=bot), _group(), _runtime())
        self.assertEqual(result, AI_ALLOWED)
        self.assertEqual(bot.calls, 0, "no Telegram lookup is needed when everyone may use AI")

    async def test_members_blocked_when_member_switch_is_off(self):
        result = await check_ai_access(_message(MEMBER_ID), _group(members=False), _runtime())
        self.assertEqual(result, AI_ADMIN_ONLY)

    async def test_admins_allowed_when_member_switch_is_off(self):
        group = _group(members=False)
        for user_id in (GROUP_ADMIN_ID, CREATOR_ID, BOT_ADMIN_ID):
            self.assertEqual(await check_ai_access(_message(user_id), group, _runtime()), AI_ALLOWED, user_id)

    async def test_anonymous_group_admin_is_allowed(self):
        message = _message(1087968824, sender_chat_id=CHAT_ID)  # GroupAnonymousBot posting as the group
        self.assertEqual(await check_ai_access(message, _group(members=False), _runtime()), AI_ALLOWED)

    async def test_another_chat_as_sender_is_not_an_admin(self):
        message = _message(MEMBER_ID, sender_chat_id=-100999)
        self.assertEqual(await check_ai_access(message, _group(members=False), _runtime()), AI_ADMIN_ONLY)

    async def test_master_switch_off_disables_ai_for_everyone(self):
        for members in (True, False):
            group = _group(ai=False, members=members)
            for user_id in (MEMBER_ID, GROUP_ADMIN_ID, BOT_ADMIN_ID):
                self.assertEqual(await check_ai_access(_message(user_id), group, _runtime()), AI_DISABLED)
        self.assertEqual(await check_ai_access(_message(MEMBER_ID), None, _runtime()), AI_DISABLED)

    async def test_telegram_failure_fails_closed(self):
        message = _message(GROUP_ADMIN_ID, bot=_FakeBot(fail=True))
        self.assertEqual(await check_ai_access(message, _group(members=False), _runtime()), AI_ADMIN_ONLY)

    async def test_missing_sender_is_blocked_when_admin_only(self):
        self.assertEqual(await check_ai_access(_message(None), _group(members=False), _runtime()), AI_ADMIN_ONLY)

    async def test_private_chat_is_limited_to_bot_admin_ids(self):
        self.assertEqual(await check_ai_access(_message(BOT_ADMIN_ID, chat_type="private"), None, _runtime()), AI_ALLOWED)
        self.assertEqual(await check_ai_access(_message(MEMBER_ID, chat_type="private"), None, _runtime()), AI_PRIVATE_DENIED)
        # a group admin has no special rights in a private chat
        self.assertEqual(await check_ai_access(_message(GROUP_ADMIN_ID, chat_type="private"), None, _runtime()), AI_PRIVATE_DENIED)
        # no configured admin ids -> nobody
        self.assertEqual(await check_ai_access(_message(BOT_ADMIN_ID, chat_type="private"), None, _runtime("")), AI_PRIVATE_DENIED)

    async def test_missing_attribute_on_old_group_object_defaults_to_open(self):
        legacy_group = SimpleNamespace(deepseek_enabled=True)
        self.assertEqual(await check_ai_access(_message(MEMBER_ID), legacy_group, _runtime()), AI_ALLOWED)


class GroupConfigPersistenceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="miyin ai test ")
        self.addCleanup(self._tmp.cleanup)
        db_path = Path(self._tmp.name) / "test.db"
        self.engine = create_async_engine(f"sqlite+aiosqlite:///{db_path.as_posix()}")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.sessions = async_sessionmaker(self.engine, expire_on_commit=False)
        self.addAsyncCleanup(self.engine.dispose)

    async def test_new_groups_keep_current_behaviour_members_allowed(self):
        async with self.sessions() as db:
            group = await ensure_group(db, CHAT_ID, "test")
            self.assertTrue(group.deepseek_enabled)
            self.assertTrue(group.ai_member_enabled)

    async def test_switch_can_be_changed_through_the_api(self):
        app = FastAPI()
        app.include_router(group_router, prefix="/api/v1")

        async def override_get_db():
            async with self.sessions() as session:
                yield session

        app.dependency_overrides[get_db] = override_get_db
        async with self.sessions() as db:
            await ensure_group(db, CHAT_ID, "test")

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.patch(f"/api/v1/groups/{CHAT_ID}", json={"ai_member_enabled": False})
            self.assertEqual(response.status_code, 200, response.text)
            self.assertFalse(response.json()["ai_member_enabled"])
            self.assertTrue(response.json()["deepseek_enabled"], "master switch must be untouched")

            listed = (await client.get("/api/v1/groups")).json()
            self.assertFalse(listed[0]["ai_member_enabled"])

        async with self.sessions() as db:
            self.assertFalse((await get_group(db, CHAT_ID)).ai_member_enabled)


if __name__ == "__main__":
    unittest.main()
