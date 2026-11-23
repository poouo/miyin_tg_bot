from pydantic import BaseModel, Field

from apps.api.app.schemas.runtime_config import AIProvider


class ModelListRequest(BaseModel):
    provider: AIProvider
    api_key: str = ""
    base_url: str = ""


class ModelListResponse(BaseModel):
    provider: str
    base_url: str
    models: list[str] = Field(default_factory=list)
