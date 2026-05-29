from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

AutoReplyParseMode = Literal["plain", "markdownv2", "html"]


class AutoReplyRuleBase(BaseModel):
    keyword: str = Field(min_length=1, max_length=255)
    reply_text: str = Field(min_length=1, max_length=4000)
    parse_mode: AutoReplyParseMode = "plain"
    delete_after_seconds: int = Field(default=0, ge=0, le=86400)
    enabled: bool = True

    @field_validator("keyword")
    @classmethod
    def validate_keyword(cls, value: str) -> str:
        parts = [item.strip() for item in value.replace("，", ",").split(",") if item.strip()]
        if not parts:
            raise ValueError("keyword must include at least one non-empty item")
        return ",".join(parts)


class AutoReplyRuleCreate(AutoReplyRuleBase):
    chat_id: int


class AutoReplyRuleUpdate(BaseModel):
    keyword: str | None = Field(default=None, min_length=1, max_length=255)
    reply_text: str | None = Field(default=None, min_length=1, max_length=4000)
    parse_mode: AutoReplyParseMode | None = None
    delete_after_seconds: int | None = Field(default=None, ge=0, le=86400)
    enabled: bool | None = None

    @field_validator("keyword")
    @classmethod
    def validate_keyword(cls, value: str | None) -> str | None:
        if value is None:
            return value
        parts = [item.strip() for item in value.replace("，", ",").split(",") if item.strip()]
        if not parts:
            raise ValueError("keyword must include at least one non-empty item")
        return ",".join(parts)


class AutoReplyRuleRead(AutoReplyRuleBase):
    id: int
    chat_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
