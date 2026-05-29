from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.db import get_db
from apps.api.app.schemas.ask import AskRequest, AskResponse
from apps.api.app.services.deepseek_client import DeepSeekClient
from apps.api.app.services.runtime_config_service import get_runtime_config

router = APIRouter(prefix="/ai", tags=["ai"])
deepseek_client = DeepSeekClient()


@router.post("/ask", response_model=AskResponse)
async def ask(payload: AskRequest, db: AsyncSession = Depends(get_db)) -> AskResponse:
    runtime = await get_runtime_config(db)
    answer = await deepseek_client.ask(payload.question, payload.system_prompt, db=db)
    return AskResponse(answer=answer, model=runtime.deepseek_model)
