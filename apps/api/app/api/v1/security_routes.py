from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.db import get_db
from apps.api.app.core.i18n import normalize_language
from apps.api.app.schemas.security import SecurityConfigRead, SecurityConfigUpdate
from apps.api.app.services.security_service import get_or_create_security_config, update_security_config
from apps.api.app.services.web_language_service import read_web_language, write_web_language

router = APIRouter(prefix="/security", tags=["security"])


def _build_response(entity, web_language: str) -> SecurityConfigRead:
    return SecurityConfigRead(
        login_ban_enabled=entity.login_ban_enabled,
        login_max_attempts=entity.login_max_attempts,
        login_ban_minutes=entity.login_ban_minutes,
        web_language=normalize_language(web_language),
        updated_at=entity.updated_at,
    )


@router.get("/login", response_model=SecurityConfigRead)
async def get_login_security(db: AsyncSession = Depends(get_db)) -> SecurityConfigRead:
    entity = await get_or_create_security_config(db)
    lang = read_web_language()
    return _build_response(entity, lang)


@router.put("/login", response_model=SecurityConfigRead)
async def update_login_security(
    payload: SecurityConfigUpdate,
    db: AsyncSession = Depends(get_db),
) -> SecurityConfigRead:
    entity = await update_security_config(db, payload)
    lang = write_web_language(payload.web_language)
    return _build_response(entity, lang)

