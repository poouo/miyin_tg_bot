from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class AdKeywordBase(BaseModel):
    keyword: str = Field(min_length=1, max_length=255)
    enabled: bool = True

    @field_validator("keyword")
    @classmethod
    def validate_keyword(cls, value: str) -> str:
        parts = [item.strip() for item in value.replace("，", ",").split(",") if item.strip()]
        if not parts:
            raise ValueError("keyword must include at least one non-empty item")
        return ",".join(parts)


class AdKeywordCreate(AdKeywordBase):
    chat_id: int


class AdKeywordUpdate(BaseModel):
    keyword: str | None = Field(default=None, min_length=1, max_length=255)
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


class AdKeywordRead(AdKeywordBase):
    id: int
    chat_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
