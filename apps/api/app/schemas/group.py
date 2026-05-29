from datetime import datetime

from pydantic import BaseModel


class GroupConfigBase(BaseModel):
    chat_id: int
    title: str = ""
    join_verification_enabled: bool = True
    keyword_filter_enabled: bool = True
    ad_block_enabled: bool = True
    anti_spam_enabled: bool = True
    auto_recover_enabled: bool = True
    deepseek_enabled: bool = True


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


class GroupConfigRead(GroupConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

