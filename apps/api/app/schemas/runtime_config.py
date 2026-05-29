from datetime import datetime

from pydantic import BaseModel, Field


class RuntimeConfigRead(BaseModel):
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
    updated_at: datetime | None = None


class RuntimeConfigUpdate(BaseModel):
    telegram_bot_token: str = ""
    telegram_bot_username: str = ""
    telegram_admin_ids: str = ""
    deepseek_api_key: str = ""
    deepseek_base_url: str = Field(default="https://api.deepseek.com")
    deepseek_model: str = Field(default="deepseek-chat")
    deepseek_timeout_sec: int = Field(default=30, ge=3, le=120)
    join_verify_timeout_sec: int = Field(default=180, ge=30, le=3600)
    spam_window_sec: int = Field(default=10, ge=2, le=120)
    spam_max_messages: int = Field(default=6, ge=2, le=30)
    ad_regex: str = Field(default=r"(t\.me/|telegram\.me/|vx|wechat|free|bet|promo)")
