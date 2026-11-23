from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

AIProvider = Literal["deepseek", "opencode", "custom"]


class RuntimeConfigRead(BaseModel):
    telegram_bot_token: str
    telegram_bot_username: str
    telegram_admin_ids: str
    deepseek_api_key: str
    deepseek_base_url: str
    deepseek_model: str
    deepseek_timeout_sec: int
    ai_provider: AIProvider
    ai_temperature: float
    ai_max_tokens: int
    ai_system_prompt: str
    opencode_api_key: str
    opencode_base_url: str
    opencode_model: str
    custom_api_key: str
    custom_base_url: str
    custom_model: str
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
    ai_provider: AIProvider = "deepseek"
    ai_temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    ai_max_tokens: int = Field(default=0, ge=0, le=32000)
    ai_system_prompt: str = ""
    opencode_api_key: str = ""
    opencode_base_url: str = Field(default="https://opencode.ai/inference/openai/v1")
    opencode_model: str = Field(default="deepseek-v4.1-flash")
    custom_api_key: str = ""
    custom_base_url: str = ""
    custom_model: str = ""
    join_verify_timeout_sec: int = Field(default=180, ge=30, le=3600)
    spam_window_sec: int = Field(default=10, ge=2, le=120)
    spam_max_messages: int = Field(default=6, ge=2, le=30)
    ad_regex: str = ""
