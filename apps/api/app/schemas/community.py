from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

WarnAction = Literal["mute", "kick", "ban"]


class CommunityConfigRead(BaseModel):
    chat_id: int
    rules_text: str = ""
    welcome_enabled: bool = True
    goodbye_enabled: bool = False
    clean_welcome: bool = True
    welcome_text: str = ""
    goodbye_text: str = ""
    warn_limit: int = 3
    warn_action: WarnAction = "mute"
    warn_mute_minutes: int = 60
    warn_ban_minutes: int = 1440
    reports_enabled: bool = True
    lock_links: bool = False
    lock_forwards: bool = False
    lock_media: bool = False
    lock_stickers: bool = False
    lock_commands: bool = False
    log_enabled: bool = False
    log_chat_id: int = 0
    disabled_commands: list[str] = []


class CommunityConfigUpdate(BaseModel):
    rules_text: str | None = Field(default=None, max_length=12000)
    welcome_enabled: bool | None = None
    goodbye_enabled: bool | None = None
    clean_welcome: bool | None = None
    welcome_text: str | None = Field(default=None, max_length=4000)
    goodbye_text: str | None = Field(default=None, max_length=4000)
    warn_limit: int | None = Field(default=None, ge=1, le=20)
    warn_action: WarnAction | None = None
    warn_mute_minutes: int | None = Field(default=None, ge=1, le=10080)
    warn_ban_minutes: int | None = Field(default=None, ge=1, le=10080)
    reports_enabled: bool | None = None
    lock_links: bool | None = None
    lock_forwards: bool | None = None
    lock_media: bool | None = None
    lock_stickers: bool | None = None
    lock_commands: bool | None = None
    log_enabled: bool | None = None
    log_chat_id: int | None = None
    disabled_commands: list[str] | None = None


class NoteRead(BaseModel):
    id: int
    chat_id: int
    name: str
    text: str
    parse_mode: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NoteWrite(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    text: str = Field(min_length=1, max_length=4000)
    parse_mode: Literal["plain", "markdownv2", "html"] = "plain"


class RssRead(BaseModel):
    id: int
    chat_id: int
    url: str
    title: str
    last_entry_id: str
    enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RssWrite(BaseModel):
    url: str = Field(min_length=8, max_length=2000)
    title: str = Field(default="", max_length=255)


class GlobalBanRead(BaseModel):
    id: int
    user_id: int
    reason: str
    admin_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GlobalBanWrite(BaseModel):
    user_id: int
    admin_id: int = 0
    reason: str = Field(default="", max_length=1000)
