from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    system_prompt: str | None = None


class AskResponse(BaseModel):
    answer: str
    model: str

