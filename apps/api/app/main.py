from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles

from apps.api.app.api.v1.admin_routes import router as admin_router
from apps.api.app.api.v1.api_router import api_router
from apps.api.app.core.auth import require_admin_api
from apps.api.app.core.db import init_db
from packages.shared.shared.config.settings import settings
from packages.shared.shared.logging.logger import setup_logging

setup_logging()

app = FastAPI(title=settings.project_name)
app.mount("/static", StaticFiles(directory="apps/api/app/static"), name="static")

app.include_router(admin_router)
app.include_router(api_router, dependencies=[Depends(require_admin_api)])


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()


@app.get("/healthz")
async def healthz() -> dict:
    return {"ok": True, "service": settings.project_name}
