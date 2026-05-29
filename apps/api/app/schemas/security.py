from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SecurityConfigRead(BaseModel):
    login_ban_enabled: bool
    login_max_attempts: int
    login_ban_minutes: int
    web_language: str
    updated_at: datetime

    class Config:
        from_attributes = True


class SecurityConfigUpdate(BaseModel):
    login_ban_enabled: bool
    login_max_attempts: int = Field(ge=2, le=20)
    login_ban_minutes: int = Field(ge=1, le=120)
    web_language: Literal["zh", "en"] = "zh"
