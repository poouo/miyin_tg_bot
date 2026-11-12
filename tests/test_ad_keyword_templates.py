import tempfile
import unittest
from pathlib import Path

import httpx
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import apps.api.app.models.entities  # noqa: F401  (registers tables on Base)
from apps.api.app.api.v1.ad_keyword_routes import router as ad_keyword_router
from apps.api.app.core.db import get_db
from apps.api.app.core.i18n import TRANSLATIONS
from apps.api.app.models.base import Base
from apps.api.app.schemas.ad_keyword import AdKeywordCreate
from apps.api.app.services.ad_keyword_service import create_ad_keyword, list_ad_keywords, match_ad_keyword
from apps.api.app.services.ad_keyword_templates import (
    MAX_RULE_KEYWORD_LENGTH,
    RISK_STANDARD,
    RISK_STRICT,
    TEMPLATES,
    apply_templates,
    chunk_keywords,
    describe_templates,
)

CHAT_ID = -1001234567890


class TemplateDataTests(unittest.TestCase):
    def test_template_ids_are_unique_and_risk_is_valid(self):
        ids = [template.id for template in TEMPLATES]
        self.assertEqual(len(ids), len(set(ids)))
        for template in TEMPLATES:
            self.assertIn(template.risk, {RISK_STANDARD, RISK_STRICT})

    def test_keywords_are_clean(self):
        for template in TEMPLATES:
            self.assertGreaterEqual(len(template.keywords), 10, template.id)
            self.assertEqual(len(template.keywords), len(set(template.keywords)), template.id)
            for keyword in template.keywords:
                self.assertEqual(keyword, keyword.strip().lower(), (template.id, keyword))
                self.assertNotIn(",", keyword, (template.id, keyword))
                self.assertNotIn("，", keyword, (template.id, keyword))
                self.assertGreaterEqual(len(keyword), 2, (template.id, keyword))

    def test_every_template_has_text_in_every_language(self):
        ui_keys = [
            "ad_template_import", "ad_template_title", "ad_template_hint",
            "ad_template_risk_standard", "ad_template_risk_strict", "ad_template_words",
            "ad_template_imported", "ad_template_apply", "ad_template_none_selected",
            "ad_template_done", "ad_template_added", "ad_template_skipped", "ad_template_rules",
        ]
        for lang, table in TRANSLATIONS.items():
            for key in ui_keys:
                self.assertTrue(table.get(key), (lang, key))
            for template in TEMPLATES:
                self.assertTrue(table.get(f"ad_tpl_{template.id}_name"), (lang, template.id))
                self.assertTrue(table.get(f"ad_tpl_{template.id}_desc"), (lang, template.id))

    def test_chunking_keeps_every_keyword_and_respects_length(self):
        for template in TEMPLATES:
            chunks = chunk_keywords(list(template.keywords))
            joined = ",".join(chunks).split(",")
            self.assertEqual(joined, list(template.keywords))
            for chunk in chunks:
                self.assertLessEqual(len(chunk), MAX_RULE_KEYWORD_LENGTH)
        self.assertEqual(chunk_keywords([]), [])
        self.assertEqual(chunk_keywords(["aa", "bb", "cc"], max_length=5), ["aa,bb", "cc"])


class TemplateDatabaseTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="miyin tpl test ")
        self.addCleanup(self._tmp.cleanup)
        db_path = Path(self._tmp.name) / "test.db"
        self.engine = create_async_engine(f"sqlite+aiosqlite:///{db_path.as_posix()}")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.sessions = async_sessionmaker(self.engine, expire_on_commit=False)
        self.addAsyncCleanup(self.engine.dispose)

    async def test_apply_creates_rules_and_they_match_messages(self):
        async with self.sessions() as db:
            result = await apply_templates(db, CHAT_ID, ["gambling", "adult"], mute_user=True, delete_message=True)
            total = len(TEMPLATES[0].keywords) + len(next(t for t in TEMPLATES if t.id == "adult").keywords)
            self.assertEqual(result["added_keywords"], total)
            self.assertEqual(result["skipped_keywords"], 0)
            self.assertGreaterEqual(result["created_rules"], 2)

            rules = await list_ad_keywords(db, CHAT_ID)
            self.assertEqual(len(rules), result["created_rules"])
            self.assertTrue(all(rule.mute_user and rule.delete_message and rule.enabled for rule in rules))
            self.assertTrue(all(len(rule.keyword) <= MAX_RULE_KEYWORD_LENGTH for rule in rules))

            self.assertIsNotNone(await match_ad_keyword(db, CHAT_ID, "欢迎来玩百家乐，首充送彩金"))
            self.assertIsNotNone(await match_ad_keyword(db, CHAT_ID, "Best CASINO bonus"))
            self.assertIsNone(await match_ad_keyword(db, CHAT_ID, "大家早上好，今天天气不错"))

    async def test_applying_twice_and_existing_keywords_are_skipped(self):
        async with self.sessions() as db:
            await create_ad_keyword(db, AdKeywordCreate(chat_id=CHAT_ID, keyword="菠菜,我的自定义词"))
            first = await apply_templates(db, CHAT_ID, ["gambling"])
            gambling = TEMPLATES[0]
            self.assertEqual(first["skipped_keywords"], 1)
            self.assertEqual(first["added_keywords"], len(gambling.keywords) - 1)

            second = await apply_templates(db, CHAT_ID, ["gambling", "gambling"])
            self.assertEqual(second["created_rules"], 0)
            self.assertEqual(second["added_keywords"], 0)
            self.assertEqual(second["skipped_keywords"], len(gambling.keywords))

            summary = {item["id"]: item for item in await describe_templates(db, CHAT_ID)}
            self.assertEqual(summary["gambling"]["imported_count"], len(gambling.keywords))
            self.assertEqual(summary["adult"]["imported_count"], 0)

    async def test_rules_are_per_group(self):
        async with self.sessions() as db:
            await apply_templates(db, CHAT_ID, ["en_spam"])
            self.assertEqual(await list_ad_keywords(db, CHAT_ID + 1), [])

    async def test_unknown_template_is_rejected_without_writing(self):
        async with self.sessions() as db:
            with self.assertRaises(ValueError):
                await apply_templates(db, CHAT_ID, ["gambling", "nope"])
            self.assertEqual(await list_ad_keywords(db, CHAT_ID), [])

    async def test_http_routes(self):
        app = FastAPI()
        app.include_router(ad_keyword_router, prefix="/api/v1")

        async def override_get_db():
            async with self.sessions() as session:
                yield session

        app.dependency_overrides[get_db] = override_get_db
        base = f"/api/v1/groups/{CHAT_ID}/ad-keywords"
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            listing = await client.get(f"{base}/templates")
            self.assertEqual(listing.status_code, 200)
            self.assertEqual([item["id"] for item in listing.json()], [t.id for t in TEMPLATES])
            self.assertTrue(all(item["imported_count"] == 0 for item in listing.json()))

            applied = await client.post(f"{base}/templates/apply", json={"template_ids": ["tg_promo"], "ban_user": True, "delete_message": False})
            self.assertEqual(applied.status_code, 200, applied.text)
            self.assertEqual(applied.json()["skipped_keywords"], 0)

            rules = (await client.get(base)).json()
            self.assertTrue(rules)
            self.assertTrue(all(rule["ban_user"] and not rule["delete_message"] for rule in rules))

            # no action selected / both penalties / unknown id / empty selection
            for body in (
                {"template_ids": ["adult"], "delete_message": False},
                {"template_ids": ["adult"], "mute_user": True, "ban_user": True},
                {"template_ids": ["nope"]},
                {"template_ids": []},
            ):
                response = await client.post(f"{base}/templates/apply", json=body)
                self.assertEqual(response.status_code, 422, body)

            # the plain CRUD routes still work next to /templates
            created = await client.post(base, json={"chat_id": CHAT_ID, "keyword": "手动添加"})
            self.assertEqual(created.status_code, 200)
            removed = await client.delete(f"{base}/{created.json()['id']}")
            self.assertEqual(removed.status_code, 200)


if __name__ == "__main__":
    unittest.main()
