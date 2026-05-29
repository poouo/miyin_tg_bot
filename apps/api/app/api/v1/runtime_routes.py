from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.db import get_db
from apps.api.app.schemas.runtime_config import RuntimeConfigRead, RuntimeConfigUpdate
from apps.api.app.services.runtime_config_service import get_runtime_config, update_runtime_config

router = APIRouter(prefix="/runtime", tags=["runtime"])


def _to_read_model(config) -> RuntimeConfigRead:
    return RuntimeConfigRead(
        telegram_bot_token=config.telegram_bot_token,
        telegram_bot_username=config.telegram_bot_username,
        telegram_admin_ids=config.telegram_admin_ids,
        deepseek_api_key=config.deepseek_api_key,
        deepseek_base_url=config.deepseek_base_url,
        deepseek_model=config.deepseek_model,
        deepseek_timeout_sec=config.deepseek_timeout_sec,
        join_verify_timeout_sec=config.join_verify_timeout_sec,
        spam_window_sec=config.spam_window_sec,
        spam_max_messages=config.spam_max_messages,
        ad_regex=config.ad_regex,
        updated_at=config.updated_at,
    )


@router.get("", response_model=RuntimeConfigRead)
async def get_runtime(db: AsyncSession = Depends(get_db)) -> RuntimeConfigRead:
    config = await get_runtime_config(db)
    return _to_read_model(config)


@router.put("", response_model=RuntimeConfigRead)
async def put_runtime(payload: RuntimeConfigUpdate, db: AsyncSession = Depends(get_db)) -> RuntimeConfigRead:
    config = await update_runtime_config(db, payload.model_dump())
    return _to_read_model(config)
