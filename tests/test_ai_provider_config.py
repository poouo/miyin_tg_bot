import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import apps.api.app.models.entities  # noqa: F401  (registers tables on Base)
from apps.api.app.api.v1.ai_routes import router as ai_router
from apps.api.app.api.v1.runtime_routes import router as runtime_router
from apps.api.app.core.db import get_db
from apps.api.app.models.base import Base
from apps.api.app.services import runtime_config_service as config_service
from apps.api.app.services.ai_models import _extract_model_ids, fetch_model_ids
from apps.api.app.services.deepseek_client import DeepSeekClient
from apps.api.app.services.runtime_config_service import (
    AI_PROVIDERS,
    CONFIG_DEFAULTS,
    DEFAULT_AI_PROVIDER,
    RuntimeConfig,
    _build_runtime,
)

OPENCODE_DEFAULT_URL = "https://opencode.ai/inference/openai/v1"


def _build(**overrides):
    data = dict(CONFIG_DEFAULTS)
    data.update(overrides)
    return _build_runtime(data, None)


def _config(**overrides):
    base = dict(
        telegram_bot_token="",
        telegram_bot_username="bot",
        telegram_admin_ids="",
        deepseek_api_key="",
        deepseek_base_url="https://api.deepseek.com",
        deepseek_model="deepseek-chat",
        deepseek_timeout_sec=30,
        join_verify_timeout_sec=180,
        spam_window_sec=10,
        spam_max_messages=5,
        ad_regex="",
    )
    base.update(overrides)
    return RuntimeConfig(**base)


class ProviderResolutionTests(unittest.TestCase):
    def test_default_provider_is_deepseek(self):
        config = _build()
        self.assertEqual(config.ai_provider, DEFAULT_AI_PROVIDER)
        credentials = config.ai_credentials
        self.assertEqual(credentials.provider, "deepseek")
        self.assertEqual(credentials.label, "DeepSeek")
        self.assertEqual(credentials.base_url, "https://api.deepseek.com")
        self.assertEqual(credentials.model, "deepseek-chat")

    def test_opencode_uses_its_own_credentials(self):
        config = _build(ai_provider="opencode", opencode_api_key="sk-opencode", deepseek_api_key="sk-deepseek")
        credentials = config.ai_credentials
        self.assertEqual(credentials.provider, "opencode")
        self.assertEqual(credentials.label, "OpenCode")
        self.assertEqual(credentials.api_key, "sk-opencode")
        self.assertEqual(credentials.base_url, OPENCODE_DEFAULT_URL)
        self.assertEqual(credentials.model, "deepseek-v4.1-flash")

    def test_custom_provider_uses_its_own_credentials(self):
        config = _build(
            ai_provider="custom",
            custom_api_key="sk-custom",
            custom_base_url="https://example.com/v1",
            custom_model="my-model",
        )
        credentials = config.ai_credentials
        self.assertEqual(credentials.provider, "custom")
        self.assertEqual(credentials.api_key, "sk-custom")
        self.assertEqual(credentials.base_url, "https://example.com/v1")
        self.assertEqual(credentials.model, "my-model")

    def test_unknown_provider_falls_back_to_default(self):
        config = _build(ai_provider="openrouter")
        self.assertEqual(config.ai_provider, DEFAULT_AI_PROVIDER)
        self.assertEqual(config.ai_credentials.provider, DEFAULT_AI_PROVIDER)

    def test_provider_is_normalized(self):
        config = _build(ai_provider="  OpenCode ")
        self.assertEqual(config.ai_provider, "opencode")

    def test_general_options_are_shared_between_providers(self):
        config = _build(ai_provider="custom", ai_temperature="1.1", ai_max_tokens="2048", ai_system_prompt="  be concise  ")
        credentials = config.ai_credentials
        self.assertAlmostEqual(credentials.temperature, 1.1)
        self.assertEqual(credentials.max_tokens, 2048)
        self.assertEqual(credentials.system_prompt, "be concise")

    def test_numeric_values_are_clamped(self):
        high = _build(ai_temperature="9", ai_max_tokens="999999")
        self.assertEqual(high.ai_temperature, 2.0)
        self.assertEqual(high.ai_max_tokens, 32000)
        low = _build(ai_temperature="-1", ai_max_tokens="-5")
        self.assertEqual(low.ai_temperature, 0.0)
        self.assertEqual(low.ai_max_tokens, 0)

    def test_invalid_numbers_fall_back_to_defaults(self):
        config = _build(ai_temperature="abc", ai_max_tokens="abc")
        self.assertEqual(config.ai_temperature, 0.3)
        self.assertEqual(config.ai_max_tokens, 0)

    def test_provider_defaults_are_registered(self):
        expected = {
            "ai_provider",
            "ai_temperature",
            "ai_max_tokens",
            "ai_system_prompt",
            "opencode_api_key",
            "opencode_base_url",
            "opencode_model",
            "custom_api_key",
            "custom_base_url",
            "custom_model",
        }
        self.assertTrue(expected.issubset(CONFIG_DEFAULTS))
        self.assertIn(CONFIG_DEFAULTS["ai_provider"], AI_PROVIDERS)
        self.assertEqual(DEFAULT_AI_PROVIDER, "deepseek")


class UpdateRuntimeConfigTests(unittest.TestCase):
    def tearDown(self):
        config_service._runtime_cache = None
        config_service._runtime_cache_at = 0.0

    def test_update_persists_and_normalizes_provider_settings(self):
        async def scenario():
            with tempfile.TemporaryDirectory() as tmp_dir:
                engine = create_async_engine(f"sqlite+aiosqlite:///{Path(tmp_dir) / 'test.db'}")
                try:
                    async with engine.begin() as conn:
                        await conn.run_sync(Base.metadata.create_all)
                    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
                        return await config_service.update_runtime_config(
                            session,
                            {
                                "ai_provider": "  OPENCODE ",
                                "opencode_api_key": " sk-opencode ",
                                "opencode_model": "deepseek-v4-pro",
                                "ai_temperature": "0.9",
                                "ai_max_tokens": 512,
                                "ai_system_prompt": "answer briefly",
                            },
                        )
                finally:
                    await engine.dispose()

        config = asyncio.run(scenario())
        self.assertEqual(config.ai_provider, "opencode")
        credentials = config.ai_credentials
        self.assertEqual(credentials.api_key, "sk-opencode")
        self.assertEqual(credentials.model, "deepseek-v4-pro")
        self.assertAlmostEqual(credentials.temperature, 0.9)
        self.assertEqual(credentials.max_tokens, 512)
        self.assertEqual(credentials.system_prompt, "answer briefly")

    def test_invalid_provider_value_is_stored_as_default(self):
        async def scenario():
            with tempfile.TemporaryDirectory() as tmp_dir:
                engine = create_async_engine(f"sqlite+aiosqlite:///{Path(tmp_dir) / 'test.db'}")
                try:
                    async with engine.begin() as conn:
                        await conn.run_sync(Base.metadata.create_all)
                    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
                        return await config_service.update_runtime_config(session, {"ai_provider": "openrouter"})
                finally:
                    await engine.dispose()

        config = asyncio.run(scenario())
        self.assertEqual(config.ai_provider, DEFAULT_AI_PROVIDER)


class _FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.request = httpx.Request("POST", "https://example.invalid/chat/completions")

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("bad response", request=self.request, response=self)

    def json(self):
        return self._payload


class _FakeAsyncClient:
    calls: list[dict] = []
    payload = {"choices": [{"message": {"content": " hello "}}]}
    status_code = 200

    def __init__(self, timeout=None):
        self.timeout = timeout

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        return False

    async def post(self, url, json=None, headers=None):
        type(self).calls.append({"url": url, "json": json, "headers": headers, "timeout": self.timeout})
        return _FakeResponse(type(self).payload, type(self).status_code)


class AskRequestTests(unittest.TestCase):
    def setUp(self):
        _FakeAsyncClient.calls = []
        _FakeAsyncClient.payload = {"choices": [{"message": {"content": " hello "}}]}
        _FakeAsyncClient.status_code = 200

    async def _ask(self, config, question="你好", system_prompt=None):
        with patch("apps.api.app.services.deepseek_client.httpx.AsyncClient", _FakeAsyncClient), patch(
            "apps.api.app.services.deepseek_client.get_runtime_config",
            AsyncMock(return_value=config),
        ):
            return await DeepSeekClient().ask(question, system_prompt)

    def test_opencode_request_is_openai_compatible(self):
        config = _config(ai_provider="opencode", opencode_api_key="sk-open", opencode_model="deepseek-v4-pro")
        answer = asyncio.run(self._ask(config))

        self.assertEqual(answer, "hello")
        call = _FakeAsyncClient.calls[-1]
        self.assertEqual(call["url"], f"{OPENCODE_DEFAULT_URL}/chat/completions")
        self.assertEqual(call["headers"]["Authorization"], "Bearer sk-open")
        self.assertEqual(call["json"]["model"], "deepseek-v4-pro")
        self.assertAlmostEqual(call["json"]["temperature"], 0.3)
        self.assertNotIn("max_tokens", call["json"])
        self.assertEqual(call["timeout"], 30)

    def test_custom_provider_trims_trailing_slash(self):
        config = _config(ai_provider="custom", custom_api_key="sk-c", custom_base_url="https://example.com/v1/", custom_model="m")
        asyncio.run(self._ask(config))
        self.assertEqual(_FakeAsyncClient.calls[-1]["url"], "https://example.com/v1/chat/completions")

    def test_general_options_reach_request(self):
        config = _config(
            ai_provider="opencode",
            opencode_api_key="sk-open",
            ai_max_tokens=256,
            ai_system_prompt="系统提示",
        )
        asyncio.run(self._ask(config))
        payload = _FakeAsyncClient.calls[-1]["json"]
        self.assertEqual(payload["max_tokens"], 256)
        self.assertEqual(payload["messages"][0], {"role": "system", "content": "系统提示"})

    def test_explicit_system_prompt_wins(self):
        config = _config(ai_provider="opencode", opencode_api_key="sk-open", ai_system_prompt="后台提示")
        asyncio.run(self._ask(config, system_prompt="调用方提示"))
        messages = _FakeAsyncClient.calls[-1]["json"]["messages"]
        self.assertEqual(messages[0]["content"], "调用方提示")

    def test_missing_key_returns_hint_without_request(self):
        config = _config(ai_provider="opencode")
        answer = asyncio.run(self._ask(config))
        self.assertIn("OpenCode", answer)
        self.assertIn("API Key", answer)
        self.assertEqual(_FakeAsyncClient.calls, [])

    def test_http_error_returns_readable_message(self):
        _FakeAsyncClient.status_code = 401
        config = _config(ai_provider="opencode", opencode_api_key="sk-bad")
        answer = asyncio.run(self._ask(config))
        self.assertIn("401", answer)

    def test_unexpected_payload_returns_readable_message(self):
        _FakeAsyncClient.payload = {"error": "boom"}
        config = _config(ai_provider="opencode", opencode_api_key="sk-open")
        answer = asyncio.run(self._ask(config))
        self.assertIn("Chat Completions", answer)


class ExtractModelIdsTests(unittest.TestCase):
    def test_openai_data_shape(self):
        payload = {"object": "list", "data": [{"id": "m-b"}, {"id": "m-a"}, {"id": "m-b"}]}
        self.assertEqual(_extract_model_ids(payload), ["m-b", "m-a"])

    def test_models_key_and_string_list(self):
        self.assertEqual(_extract_model_ids({"models": ["z", "y"]}), ["z", "y"])
        self.assertEqual(_extract_model_ids(["only"]), ["only"])

    def test_single_model_object(self):
        self.assertEqual(_extract_model_ids({"id": "solo"}), ["solo"])

    def test_unusable_payloads(self):
        for payload in ({"error": "x"}, {"data": "nope"}, None, 42):
            self.assertEqual(_extract_model_ids(payload), [], payload)


class _FakeModelResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class _FakeModelClient:
    responses: dict = {}
    requested: list = []

    def __init__(self, timeout=None):
        self.timeout = timeout

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        return False

    async def get(self, url, headers=None):
        type(self).requested.append(url)
        response = type(self).responses.get(url)
        if response is None:
            raise RuntimeError("connection refused")
        return response


class FetchModelIdsTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        _FakeModelClient.responses = {}
        _FakeModelClient.requested = []
        patcher = patch("apps.api.app.services.ai_models.httpx.AsyncClient", _FakeModelClient)
        patcher.start()
        self.addCleanup(patcher.stop)

    async def test_openai_compatible_endpoint(self):
        _FakeModelClient.responses["https://api.deepseek.com/models"] = _FakeModelResponse(
            200, {"data": [{"id": "deepseek-reasoner"}, {"id": "deepseek-chat"}]}
        )
        models, url = await fetch_model_ids("https://api.deepseek.com", "sk-x")
        self.assertEqual(models, ["deepseek-chat", "deepseek-reasoner"])
        self.assertEqual(url, "https://api.deepseek.com/models")

    async def test_opencode_falls_back_outside_openai_prefix(self):
        _FakeModelClient.responses["https://opencode.ai/inference/openai/v1/models"] = _FakeModelResponse(404, {})
        _FakeModelClient.responses["https://opencode.ai/inference/v1/models"] = _FakeModelResponse(
            200, {"data": [{"id": "z-model"}, {"id": "a-model"}]}
        )
        models, url = await fetch_model_ids("https://opencode.ai/inference/openai/v1", "sk-x")
        self.assertEqual(models, ["a-model", "z-model"])
        self.assertEqual(url, "https://opencode.ai/inference/v1/models")
        self.assertEqual(
            _FakeModelClient.requested,
            [
                "https://opencode.ai/inference/openai/v1/models",
                "https://opencode.ai/inference/v1/models",
            ],
        )

    async def test_missing_base_url_raises(self):
        with self.assertRaises(ValueError):
            await fetch_model_ids("   ", "sk-x")

    async def test_all_candidates_failing_raises(self):
        _FakeModelClient.responses["https://example.com/v1/models"] = _FakeModelResponse(401, {})
        with self.assertRaises(ValueError) as ctx:
            await fetch_model_ids("https://example.com/v1", "bad")
        self.assertIn("401", str(ctx.exception))


class ModelListRouteTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="miyin models test ")
        self.addCleanup(self._tmp.cleanup)
        db_path = Path(self._tmp.name) / "test.db"
        self.engine = create_async_engine(f"sqlite+aiosqlite:///{db_path.as_posix()}")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.sessions = async_sessionmaker(self.engine, expire_on_commit=False)
        self.addAsyncCleanup(self.engine.dispose)

        app = FastAPI()
        app.include_router(ai_router, prefix="/api/v1")
        app.include_router(runtime_router, prefix="/api/v1")

        async def override_get_db():
            async with self.sessions() as session:
                yield session

        app.dependency_overrides[get_db] = override_get_db
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")
        self.addAsyncCleanup(self.client.aclose)

    async def asyncTearDown(self):
        config_service._runtime_cache = None
        config_service._runtime_cache_at = 0.0

    async def test_route_uses_draft_values(self):
        with patch(
            "apps.api.app.api.v1.ai_routes.fetch_model_ids",
            AsyncMock(return_value=(["m1", "m2"], "https://custom.example/v1/models")),
        ) as mocked:
            response = await self.client.post(
                "/api/v1/ai/models",
                json={"provider": "custom", "api_key": " draft-key ", "base_url": " https://custom.example/v1 "},
            )
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["models"], ["m1", "m2"])
        self.assertEqual(body["base_url"], "https://custom.example/v1/models")
        self.assertEqual(mocked.await_args.args[0], "https://custom.example/v1")
        self.assertEqual(mocked.await_args.args[1], "draft-key")

    async def test_route_falls_back_to_saved_provider_config(self):
        async with self.sessions() as session:
            await config_service.update_runtime_config(
                session,
                {
                    "ai_provider": "opencode",
                    "opencode_api_key": "saved-key",
                    "opencode_base_url": "https://opencode.ai/inference/openai/v1",
                },
            )
        with patch(
            "apps.api.app.api.v1.ai_routes.fetch_model_ids",
            AsyncMock(return_value=(["m1"], "https://opencode.ai/inference/v1/models")),
        ) as mocked:
            response = await self.client.post("/api/v1/ai/models", json={"provider": "opencode"})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(mocked.await_args.args[0], "https://opencode.ai/inference/openai/v1")
        self.assertEqual(mocked.await_args.args[1], "saved-key")

    async def test_model_list_uses_explicit_empty_draft_key(self):
        async with self.sessions() as session:
            await config_service.update_runtime_config(session, {"custom_api_key": "saved-key"})
        with patch(
            "apps.api.app.api.v1.ai_routes.fetch_model_ids",
            AsyncMock(return_value=(["m1"], "https://example.com/v1/models")),
        ) as mocked:
            response = await self.client.post(
                "/api/v1/ai/models",
                json={"provider": "custom", "api_key": "", "base_url": "https://example.com/v1"},
            )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(mocked.await_args.args[1], "")

    async def test_runtime_patch_updates_only_submitted_fields(self):
        async with self.sessions() as session:
            await config_service.update_runtime_config(
                session, {"telegram_bot_username": "existing_bot", "deepseek_model": "old-model", "ad_regex": "example"},
            )
        with patch("apps.api.app.api.v1.runtime_routes.request_bot_reload", AsyncMock()) as reload_bot:
            ai_result = await self.client.patch("/api/v1/runtime", json={"deepseek_model": "new-model"})
            self.assertEqual(ai_result.status_code, 200, ai_result.text)
            self.assertEqual(ai_result.json()["telegram_bot_username"], "existing_bot")
            reload_bot.assert_not_awaited()
            runtime_result = await self.client.patch("/api/v1/runtime", json={"telegram_bot_username": "new_bot"})
            reload_bot.assert_awaited_once()
        self.assertEqual(runtime_result.status_code, 200, runtime_result.text)
        self.assertEqual(runtime_result.json()["deepseek_model"], "new-model")
        self.assertEqual(runtime_result.json()["ad_regex"], "example")

    async def test_route_maps_fetch_errors_to_502(self):
        with patch(
            "apps.api.app.api.v1.ai_routes.fetch_model_ids",
            AsyncMock(side_effect=ValueError("无法获取模型列表（HTTP 401）")),
        ):
            response = await self.client.post("/api/v1/ai/models", json={"provider": "deepseek"})
        self.assertEqual(response.status_code, 502, response.text)
        self.assertIn("401", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
