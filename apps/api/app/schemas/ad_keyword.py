from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator


def validate_ad_keyword_actions(
    delete_message: bool,
    mute_user: bool,
    ban_user: bool,
    apply_to_mentions: bool = False,
) -> None:
    if not (delete_message or mute_user or ban_user):
        raise ValueError("select at least one ad keyword action")
    if mute_user and ban_user:
        raise ValueError("mute_user and ban_user cannot both be enabled")
    if apply_to_mentions and not (mute_user or ban_user):
        raise ValueError("mute_user or ban_user is required when apply_to_mentions is enabled")


class AdKeywordBase(BaseModel):
    keyword: str = Field(min_length=1, max_length=255)
    enabled: bool = True
    delete_message: bool = True
    mute_user: bool = False
    mute_minutes: int = Field(default=30, ge=1, le=10080)
    ban_user: bool = False
    ban_minutes: int = Field(default=1440, ge=1, le=10080)
    apply_to_mentions: bool = False

    @field_validator("keyword")
    @classmethod
    def validate_keyword(cls, value: str) -> str:
        parts = [item.strip() for item in value.replace("，", ",").split(",") if item.strip()]
        if not parts:
            raise ValueError("keyword must include at least one non-empty item")
        return ",".join(parts)

    @model_validator(mode="after")
    def validate_actions(self) -> "AdKeywordBase":
        validate_ad_keyword_actions(
            self.delete_message,
            self.mute_user,
            self.ban_user,
            self.apply_to_mentions,
        )
        return self


class AdKeywordCreate(AdKeywordBase):
    chat_id: int


class AdKeywordUpdate(BaseModel):
    keyword: str | None = Field(default=None, min_length=1, max_length=255)
    enabled: bool | None = None
    delete_message: bool | None = None
    mute_user: bool | None = None
    mute_minutes: int | None = Field(default=None, ge=1, le=10080)
    ban_user: bool | None = None
    ban_minutes: int | None = Field(default=None, ge=1, le=10080)
    apply_to_mentions: bool | None = None

    @field_validator("keyword")
    @classmethod
    def validate_keyword(cls, value: str | None) -> str | None:
        if value is None:
            return value
        parts = [item.strip() for item in value.replace("，", ",").split(",") if item.strip()]
        if not parts:
            raise ValueError("keyword must include at least one non-empty item")
        return ",".join(parts)

    @model_validator(mode="after")
    def validate_actions(self) -> "AdKeywordUpdate":
        if self.mute_user is True and self.ban_user is True:
            raise ValueError("mute_user and ban_user cannot both be enabled")
        if self.delete_message is False and self.mute_user is False and self.ban_user is False:
            raise ValueError("select at least one ad keyword action")
        if self.apply_to_mentions is True and self.mute_user is False and self.ban_user is False:
            raise ValueError("mute_user or ban_user is required when apply_to_mentions is enabled")
        return self


class AdKeywordRead(AdKeywordBase):
    id: int
    chat_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
