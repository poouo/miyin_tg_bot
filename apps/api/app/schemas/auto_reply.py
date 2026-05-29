from datetime import datetime

from pydantic import BaseModel, Field


class AutoReplyRuleBase(BaseModel):
    keyword: str = Field(min_length=1, max_length=255)
    reply_text: str = Field(min_length=1, max_length=4000)
    delete_after_seconds: int = Field(default=0, ge=0, le=86400)
    enabled: bool = True


class AutoReplyRuleCreate(AutoReplyRuleBase):
    chat_id: int


class AutoReplyRuleUpdate(BaseModel):
    keyword: str | None = Field(default=None, min_length=1, max_length=255)
    reply_text: str | None = Field(default=None, min_length=1, max_length=4000)
    delete_after_seconds: int | None = Field(default=None, ge=0, le=86400)
    enabled: bool | None = None


class AutoReplyRuleRead(AutoReplyRuleBase):
    id: int
    chat_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
