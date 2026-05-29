from pydantic import BaseModel, Field


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=256)
    new_password: str = Field(min_length=4, max_length=256)
    confirm_password: str = Field(min_length=4, max_length=256)


class PasswordChangeResponse(BaseModel):
    ok: bool
    message: str

