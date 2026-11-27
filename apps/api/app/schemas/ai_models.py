from pydantic import BaseModel, Field

from apps.api.app.schemas.runtime_config import AIProvider


class ModelListRequest(BaseModel):
    provider: AIProvider
    api_key: str | None = None
    base_url: str | None = None


class ModelListResponse(BaseModel):
    provider: str
    base_url: str
    models: list[str] = Field(default_factory=list)
