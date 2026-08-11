from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


KeywordLegacyAction = Literal["delete", "mute", "ban"]


def validate_keyword_actions(delete_message: bool, mute_user: bool, ban_user: bool) -> None:
    if not (delete_message or mute_user or ban_user):
        raise ValueError("select at least one keyword action")
    if mute_user and ban_user:
        raise ValueError("mute_user and ban_user cannot both be enabled")


class KeywordRuleBase(BaseModel):
    keyword: str = Field(min_length=1, max_length=255)
    action: KeywordLegacyAction = "delete"
    delete_message: bool = True
    mute_user: bool = False
    mute_minutes: int = Field(default=10, ge=1, le=10080)
    ban_user: bool = False
    ban_minutes: int = Field(default=1440, ge=1, le=10080)
    enabled: bool = True

    @model_validator(mode="after")
    def validate_actions(self) -> "KeywordRuleBase":
        validate_keyword_actions(self.delete_message, self.mute_user, self.ban_user)
        return self


class KeywordRuleCreate(KeywordRuleBase):
    chat_id: int


class KeywordRuleUpdate(BaseModel):
    keyword: str | None = Field(default=None, min_length=1, max_length=255)
    action: KeywordLegacyAction | None = None
    delete_message: bool | None = None
    mute_user: bool | None = None
    mute_minutes: int | None = Field(default=None, ge=1, le=10080)
    ban_user: bool | None = None
    ban_minutes: int | None = Field(default=None, ge=1, le=10080)
    enabled: bool | None = None

    @model_validator(mode="after")
    def validate_actions(self) -> "KeywordRuleUpdate":
        if self.mute_user is True and self.ban_user is True:
            raise ValueError("mute_user and ban_user cannot both be enabled")
        if self.delete_message is False and self.mute_user is False and self.ban_user is False:
            raise ValueError("select at least one keyword action")
        return self


class KeywordRuleRead(KeywordRuleBase):
    id: int
    chat_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

