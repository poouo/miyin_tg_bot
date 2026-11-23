from dataclasses import dataclass
from datetime import datetime
import json
from time import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.db import SessionLocal
from apps.api.app.models.entities import AppSetting

AI_PROVIDER_LABELS: dict[str, str] = {
    "deepseek": "DeepSeek",
    "opencode": "OpenCode",
    "custom": "自定义接口",
}
AI_PROVIDERS: tuple[str, ...] = tuple(AI_PROVIDER_LABELS)
DEFAULT_AI_PROVIDER = "deepseek"


@dataclass(frozen=True)
class AICredentials:
    """Resolved connection settings of the active AI provider."""

    provider: str
    label: str
    api_key: str
    base_url: str
    model: str
    timeout_sec: int
    temperature: float
    max_tokens: int
    system_prompt: str


@dataclass
class RuntimeConfig:
    telegram_bot_token: str
    telegram_bot_username: str
    telegram_admin_ids: str
    deepseek_api_key: str
    deepseek_base_url: str
    deepseek_model: str
    deepseek_timeout_sec: int
    join_verify_timeout_sec: int
    spam_window_sec: int
    spam_max_messages: int
    ad_regex: str
    ai_provider: str = DEFAULT_AI_PROVIDER
    ai_temperature: float = 0.3
    ai_max_tokens: int = 0
    ai_system_prompt: str = ""
    opencode_api_key: str = ""
    opencode_base_url: str = "https://opencode.ai/inference/openai/v1"
    opencode_model: str = "deepseek-v4.1-flash"
    custom_api_key: str = ""
    custom_base_url: str = ""
    custom_model: str = ""
    updated_at: datetime | None = None

    @property
    def telegram_admin_id_list(self) -> list[int]:
        raw = self.telegram_admin_ids.strip()
        if not raw:
            return []
        if raw.startswith("[") and raw.endswith("]"):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    values: list[int] = []
                    for part in parsed:
                        try:
                            values.append(int(part))
                        except Exception:
                            continue
                    return values
                return []
            except Exception:
                return []
        values: list[int] = []
        for part in raw.split(","):
            item = part.strip()
            if not item:
                continue
            try:
                values.append(int(item))
            except Exception:
                continue
        return values

    def credentials_for(self, provider: str) -> AICredentials:
        """Resolve the saved credentials of one specific provider."""
        selected = provider if provider in AI_PROVIDERS else DEFAULT_AI_PROVIDER
        if selected == "opencode":
            api_key, base_url, model = self.opencode_api_key, self.opencode_base_url, self.opencode_model
        elif selected == "custom":
            api_key, base_url, model = self.custom_api_key, self.custom_base_url, self.custom_model
        else:
            api_key, base_url, model = self.deepseek_api_key, self.deepseek_base_url, self.deepseek_model
        return AICredentials(
            provider=selected,
            label=AI_PROVIDER_LABELS[selected],
            api_key=api_key,
            base_url=base_url,
            model=model,
            timeout_sec=self.deepseek_timeout_sec,
            temperature=self.ai_temperature,
            max_tokens=self.ai_max_tokens,
            system_prompt=self.ai_system_prompt,
        )

    @property
    def ai_credentials(self) -> AICredentials:
        """Return key / base URL / model of the provider selected in the dashboard."""
        return self.credentials_for(self.ai_provider)


CONFIG_DEFAULTS: dict[str, str] = {
    "telegram_bot_token": "",
    "telegram_bot_username": "",
    "telegram_admin_ids": "",
    "deepseek_api_key": "",
    "deepseek_base_url": "https://api.deepseek.com",
    "deepseek_model": "deepseek-chat",
    "deepseek_timeout_sec": "30",
    "join_verify_timeout_sec": "180",
    "spam_window_sec": "10",
    "spam_max_messages": "6",
    "ad_regex": "",
    "ai_provider": "deepseek",
    "ai_temperature": "0.3",
    "ai_max_tokens": "0",
    "ai_system_prompt": "",
    "opencode_api_key": "",
    "opencode_base_url": "https://opencode.ai/inference/openai/v1",
    "opencode_model": "deepseek-v4.1-flash",
    "custom_api_key": "",
    "custom_base_url": "",
    "custom_model": "",
}
LEGACY_DEFAULT_AD_REGEX = r"(t\.me/|telegram\.me/|vx|wechat|free|bet|promo)"

INT_KEYS = {
    "deepseek_timeout_sec",
    "join_verify_timeout_sec",
    "spam_window_sec",
    "spam_max_messages",
    "ai_max_tokens",
}
FLOAT_KEYS = {"ai_temperature"}
_CACHE_TTL_SEC = 2.0
_runtime_cache: RuntimeConfig | None = None
_runtime_cache_at: float = 0.0


def _normalize_float(raw: str, default: float, min_value: float, max_value: float) -> float:
    try:
        value = float(raw)
    except Exception:
        value = default
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


def _normalize_int(raw: str, default: int, min_value: int, max_value: int) -> int:
    try:
        value = int(raw)
    except Exception:
        value = default
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


async def _ensure_defaults(db: AsyncSession) -> None:
    result = await db.execute(select(AppSetting))
    existing = {row.key: row for row in result.scalars().all()}
    dirty = False
    for key, default in CONFIG_DEFAULTS.items():
        if key in existing:
            continue
        db.add(AppSetting(key=key, value=default))
        dirty = True
    legacy_ad_regex = existing.get("ad_regex")
    if legacy_ad_regex is not None and legacy_ad_regex.value == LEGACY_DEFAULT_AD_REGEX:
        legacy_ad_regex.value = ""
        dirty = True
    if dirty:
        await db.commit()


async def _get_config_map(db: AsyncSession) -> tuple[dict[str, str], datetime | None]:
    await _ensure_defaults(db)
    result = await db.execute(select(AppSetting))
    rows = result.scalars().all()
    latest: datetime | None = None
    data: dict[str, str] = {}
    for row in rows:
        data[row.key] = row.value
        if latest is None or (row.updated_at and row.updated_at > latest):
            latest = row.updated_at
    return data, latest


def _build_runtime(data: dict[str, str], updated_at: datetime | None) -> RuntimeConfig:
    deepseek_timeout = _normalize_int(data.get("deepseek_timeout_sec", ""), 30, 3, 120)
    join_timeout = _normalize_int(data.get("join_verify_timeout_sec", ""), 180, 30, 3600)
    spam_window = _normalize_int(data.get("spam_window_sec", ""), 10, 2, 120)
    spam_max = _normalize_int(data.get("spam_max_messages", ""), 6, 2, 30)
    ai_temperature = _normalize_float(data.get("ai_temperature", ""), 0.3, 0.0, 2.0)
    ai_max_tokens = _normalize_int(data.get("ai_max_tokens", ""), 0, 0, 32000)
    ai_provider = (data.get("ai_provider", "") or DEFAULT_AI_PROVIDER).strip().lower()
    if ai_provider not in AI_PROVIDERS:
        ai_provider = DEFAULT_AI_PROVIDER

    return RuntimeConfig(
        telegram_bot_token=(data.get("telegram_bot_token", "") or "").strip(),
        telegram_bot_username=(data.get("telegram_bot_username", "") or "").strip().lstrip("@"),
        telegram_admin_ids=(data.get("telegram_admin_ids", "") or "").strip(),
        deepseek_api_key=(data.get("deepseek_api_key", "") or "").strip(),
        deepseek_base_url=(data.get("deepseek_base_url", "") or "https://api.deepseek.com").strip(),
        deepseek_model=(data.get("deepseek_model", "") or "deepseek-chat").strip(),
        deepseek_timeout_sec=deepseek_timeout,
        join_verify_timeout_sec=join_timeout,
        spam_window_sec=spam_window,
        spam_max_messages=spam_max,
        ad_regex=(data.get("ad_regex", "") or "").strip(),
        ai_provider=ai_provider,
        ai_temperature=ai_temperature,
        ai_max_tokens=ai_max_tokens,
        ai_system_prompt=(data.get("ai_system_prompt", "") or "").strip(),
        opencode_api_key=(data.get("opencode_api_key", "") or "").strip(),
        opencode_base_url=(data.get("opencode_base_url", "") or "").strip(),
        opencode_model=(data.get("opencode_model", "") or "").strip(),
        custom_api_key=(data.get("custom_api_key", "") or "").strip(),
        custom_base_url=(data.get("custom_base_url", "") or "").strip(),
        custom_model=(data.get("custom_model", "") or "").strip(),
        updated_at=updated_at,
    )


async def get_runtime_config(db: AsyncSession | None = None) -> RuntimeConfig:
    global _runtime_cache, _runtime_cache_at
    now = time()
    if _runtime_cache is not None and (now - _runtime_cache_at) < _CACHE_TTL_SEC:
        return _runtime_cache

    if db is not None:
        data, updated_at = await _get_config_map(db)
        config = _build_runtime(data, updated_at)
        _runtime_cache = config
        _runtime_cache_at = now
        return config

    async with SessionLocal() as session:
        data, updated_at = await _get_config_map(session)
        config = _build_runtime(data, updated_at)
        _runtime_cache = config
        _runtime_cache_at = now
        return config


async def update_runtime_config(db: AsyncSession, payload: dict[str, str | int | float]) -> RuntimeConfig:
    global _runtime_cache, _runtime_cache_at
    await _ensure_defaults(db)
    result = await db.execute(select(AppSetting))
    rows = {item.key: item for item in result.scalars().all()}

    for key, value in payload.items():
        if key not in CONFIG_DEFAULTS:
            continue
        if key in INT_KEYS:
            try:
                normalized = str(int(value))
            except Exception:
                normalized = CONFIG_DEFAULTS[key]
        elif key in FLOAT_KEYS:
            try:
                normalized = str(float(value))
            except Exception:
                normalized = CONFIG_DEFAULTS[key]
        else:
            normalized = str(value).strip()
        if key == "ai_provider":
            normalized = normalized.lower()
            if normalized not in AI_PROVIDERS:
                normalized = DEFAULT_AI_PROVIDER
        row = rows.get(key)
        if row is None:
            row = AppSetting(key=key, value=normalized)
            db.add(row)
            rows[key] = row
        else:
            row.value = normalized

    await db.commit()
    data, updated_at = await _get_config_map(db)
    config = _build_runtime(data, updated_at)
    _runtime_cache = config
    _runtime_cache_at = time()
    return config
