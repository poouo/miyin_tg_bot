from datetime import datetime

from pydantic import BaseModel


class ModerationLogRead(BaseModel):
    id: int
    chat_id: int
    user_id: int
    username: str
    event_type: str
    detail: str
    created_at: datetime

    class Config:
        from_attributes = True


class ModerationLogWithGroupRead(ModerationLogRead):
    group_title: str = ""
