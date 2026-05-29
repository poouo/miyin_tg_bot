from datetime import datetime

from pydantic import BaseModel


class BanSanctionRead(BaseModel):
    id: int
    chat_id: int
    group_title: str = ""
    user_id: int
    reason: str
    expires_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True
