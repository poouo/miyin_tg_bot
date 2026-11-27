from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.db import get_db
from apps.api.app.schemas.ai_models import ModelListRequest, ModelListResponse
from apps.api.app.schemas.ask import AskRequest, AskResponse
from apps.api.app.services.ai_models import fetch_model_ids
from apps.api.app.services.deepseek_client import DeepSeekClient
from apps.api.app.services.runtime_config_service import get_runtime_config

router = APIRouter(prefix="/ai", tags=["ai"])
deepseek_client = DeepSeekClient()
MODEL_LIST_TIMEOUT_SEC = 20


@router.post("/ask", response_model=AskResponse)
async def ask(payload: AskRequest, db: AsyncSession = Depends(get_db)) -> AskResponse:
    runtime = await get_runtime_config(db)
    answer = await deepseek_client.ask(payload.question, payload.system_prompt, db=db)
    return AskResponse(answer=answer, model=runtime.ai_credentials.model)


@router.post("/models", response_model=ModelListResponse)
async def list_models(payload: ModelListRequest, db: AsyncSession = Depends(get_db)) -> ModelListResponse:
    """Fetch the model catalog for the provider form, using unsaved (draft) values when given."""
    runtime = await get_runtime_config(db)
    saved = runtime.credentials_for(payload.provider)
    api_key = saved.api_key if payload.api_key is None else payload.api_key.strip()
    base_url = saved.base_url if payload.base_url is None else payload.base_url.strip()
    try:
        models, used_base_url = await fetch_model_ids(
            base_url,
            api_key,
            timeout=min(runtime.deepseek_timeout_sec, MODEL_LIST_TIMEOUT_SEC),
        )
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return ModelListResponse(provider=payload.provider, base_url=used_base_url, models=models)
