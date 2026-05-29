from fastapi import APIRouter

from apps.api.app.schemas.ask import AskRequest, AskResponse
from apps.api.app.services.deepseek_client import DeepSeekClient
from packages.shared.shared.config.settings import settings

router = APIRouter(prefix="/ai", tags=["ai"])
deepseek_client = DeepSeekClient()


@router.post("/ask", response_model=AskResponse)
async def ask(payload: AskRequest) -> AskResponse:
    answer = await deepseek_client.ask(payload.question, payload.system_prompt)
    return AskResponse(answer=answer, model=settings.deepseek_model)

