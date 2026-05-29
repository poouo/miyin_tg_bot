from datetime import datetime

from pydantic import BaseModel, Field


class AdKeywordBase(BaseModel):
    keyword: str = Field(min_length=1, max_length=255)
    enabled: bool = True


class AdKeywordCreate(AdKeywordBase):
    chat_id: int


class AdKeywordUpdate(BaseModel):
    keyword: str | None = Field(default=None, min_length=1, max_length=255)
    enabled: bool | None = None


class AdKeywordRead(AdKeywordBase):
    id: int
    chat_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
