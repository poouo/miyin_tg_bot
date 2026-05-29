from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ModerationAction = Literal["kick", "ban", "mute"]


class GroupConfigBase(BaseModel):
    chat_id: int
    title: str = ""
    join_verification_enabled: bool = True
    keyword_filter_enabled: bool = True
    ad_block_enabled: bool = True
    anti_spam_enabled: bool = True
    auto_recover_enabled: bool = True
    deepseek_enabled: bool = True
    join_verify_fail_action: ModerationAction = "kick"
    join_verify_fail_mute_minutes: int = Field(default=30, ge=1, le=10080)
    join_verify_fail_ban_minutes: int = Field(default=1440, ge=1, le=10080)
    ad_block_action: ModerationAction = "mute"
    ad_block_mute_minutes: int = Field(default=30, ge=1, le=10080)
    ad_block_ban_minutes: int = Field(default=1440, ge=1, le=10080)
    anti_spam_action: ModerationAction = "mute"
    anti_spam_mute_minutes: int = Field(default=30, ge=1, le=10080)
    anti_spam_ban_minutes: int = Field(default=1440, ge=1, le=10080)


class GroupConfigCreate(GroupConfigBase):
    pass


class GroupConfigUpdate(BaseModel):
    title: str | None = None
    join_verification_enabled: bool | None = None
    keyword_filter_enabled: bool | None = None
    ad_block_enabled: bool | None = None
    anti_spam_enabled: bool | None = None
    auto_recover_enabled: bool | None = None
    deepseek_enabled: bool | None = None
    join_verify_fail_action: ModerationAction | None = None
    join_verify_fail_mute_minutes: int | None = Field(default=None, ge=1, le=10080)
    join_verify_fail_ban_minutes: int | None = Field(default=None, ge=1, le=10080)
    ad_block_action: ModerationAction | None = None
    ad_block_mute_minutes: int | None = Field(default=None, ge=1, le=10080)
    ad_block_ban_minutes: int | None = Field(default=None, ge=1, le=10080)
    anti_spam_action: ModerationAction | None = None
    anti_spam_mute_minutes: int | None = Field(default=None, ge=1, le=10080)
    anti_spam_ban_minutes: int | None = Field(default=None, ge=1, le=10080)


class GroupConfigRead(GroupConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
