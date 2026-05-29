from fastapi import APIRouter

from apps.api.app.api.v1.ai_routes import router as ai_router
from apps.api.app.api.v1.group_routes import router as group_router
from apps.api.app.api.v1.keyword_routes import router as keyword_router
from apps.api.app.api.v1.log_routes import router as log_router
from apps.api.app.api.v1.security_routes import router as security_router
from apps.api.app.api.v1.update_routes import router as update_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(group_router)
api_router.include_router(keyword_router)
api_router.include_router(log_router)
api_router.include_router(ai_router)
api_router.include_router(update_router)
api_router.include_router(security_router)
