from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    app_env: str = "dev"
    log_level: str = "INFO"
    project_name: str = "miyin_tg_bot"

    telegram_bot_token: str = ""
    telegram_bot_username: str = ""
    telegram_admin_ids: List[int] = Field(default_factory=list)

    database_url: str = "sqlite+aiosqlite:///./data/miyin.db"
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"
    deepseek_timeout_sec: int = 30

    web_host: str = "0.0.0.0"
    web_port: int = 9800
    web_admin_password: str = "admin123456"
    web_auth_secret: str = "replace_with_long_random_string"
    web_token_expire_days: int = 10

    join_verify_timeout_sec: int = 180
    spam_window_sec: int = 10
    spam_max_messages: int = 6
    ad_regex: str = r"(t\.me/|telegram\.me/|vx|wechat|free|bet|promo)"

    @field_validator("telegram_admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, value: str | List[int]) -> List[int]:
        if isinstance(value, list):
            return value
        if not value:
            return []
        return [int(item.strip()) for item in value.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
