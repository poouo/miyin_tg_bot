from datetime import datetime

from pydantic import BaseModel, Field


class KeywordRuleBase(BaseModel):
    keyword: str = Field(min_length=1, max_length=255)
    action: str = Field(default="delete")
    mute_minutes: int = Field(default=10, ge=1, le=10080)
    enabled: bool = True


class KeywordRuleCreate(KeywordRuleBase):
    chat_id: int


class KeywordRuleUpdate(BaseModel):
    keyword: str | None = Field(default=None, min_length=1, max_length=255)
    action: str | None = None
    mute_minutes: int | None = Field(default=None, ge=1, le=10080)
    enabled: bool | None = None


class KeywordRuleRead(KeywordRuleBase):
    id: int
    chat_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

