from fastapi import Depends, FastAPI, Response
from fastapi.staticfiles import StaticFiles

from apps.api.app.api.v1.admin_routes import router as admin_router
from apps.api.app.api.v1.api_router import api_router
from apps.api.app.core.auth import require_admin_api
from apps.api.app.core.db import get_db, init_db
from apps.api.app.services.admin_password_service import validate_admin_credentials
from apps.api.app.services.runtime_health import bot_health, database_healthy
from packages.shared.shared.config.settings import settings
from packages.shared.shared.logging.logger import setup_logging

setup_logging()

app = FastAPI(title=settings.project_name)
app.mount("/static", StaticFiles(directory="apps/api/app/static"), name="static")

app.include_router(admin_router)
app.include_router(api_router, dependencies=[Depends(require_admin_api)])


@app.on_event("startup")
async def on_startup() -> None:
    validate_admin_credentials()
    await init_db()


@app.get("/healthz")
async def healthz(response: Response, db=Depends(get_db)) -> dict:
    ok = await database_healthy(db) and bot_health()["state"] in {"online", "not_configured"}
    if not ok:
        response.status_code = 503
    return {"ok": ok, "service": settings.project_name}
