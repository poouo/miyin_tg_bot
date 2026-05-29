from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.db import get_db
from apps.api.app.schemas.security import SecurityConfigRead, SecurityConfigUpdate
from apps.api.app.services.security_service import get_or_create_security_config, update_security_config

router = APIRouter(prefix="/security", tags=["security"])


@router.get("/login", response_model=SecurityConfigRead)
async def get_login_security(db: AsyncSession = Depends(get_db)) -> SecurityConfigRead:
    return await get_or_create_security_config(db)


@router.put("/login", response_model=SecurityConfigRead)
async def update_login_security(
    payload: SecurityConfigUpdate,
    db: AsyncSession = Depends(get_db),
) -> SecurityConfigRead:
    return await update_security_config(db, payload)

