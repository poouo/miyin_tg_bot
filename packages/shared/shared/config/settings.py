import json
from functools import lru_cache
from typing import Annotated, List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    app_env: str = "dev"
    log_level: str = "INFO"
    project_name: str = "miyin_tg_bot"

    telegram_bot_token: str = ""
    telegram_bot_username: str = ""
    telegram_admin_ids: Annotated[List[int], NoDecode] = Field(default_factory=list)

    database_url: str = "sqlite+aiosqlite:///./data/miyin.db"
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"
    deepseek_timeout_sec: int = 30

    web_host: str = "0.0.0.0"
    web_port: int = 9800
    web_admin_password: str = "admin"
    web_auth_secret: str = "replace_with_long_random_string"
    web_token_expire_days: int = 10

    join_verify_timeout_sec: int = 180
    spam_window_sec: int = 10
    spam_max_messages: int = 6
    ad_regex: str = r"(t\.me/|telegram\.me/|vx|wechat|free|bet|promo)"

    @field_validator("telegram_admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, value: str | List[int] | None) -> List[int]:
        if isinstance(value, list):
            return [int(item) for item in value]
        if not value:
            return []
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return []
            # Support both JSON array: [123,456] and CSV: 123,456
            if raw.startswith("[") and raw.endswith("]"):
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [int(item) for item in parsed]
                raise ValueError("telegram_admin_ids JSON must be an array")
            return [int(item.strip()) for item in raw.split(",") if item.strip()]
        return [int(value)]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
