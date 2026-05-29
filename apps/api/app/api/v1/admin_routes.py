from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.db import get_db
from apps.api.app.services.group_service import list_groups
from apps.api.app.services.stats_service import dashboard_stats

router = APIRouter(tags=["admin"])
templates = Jinja2Templates(directory="apps/api/app/templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: AsyncSession = Depends(get_db)) -> HTMLResponse:
    stats = await dashboard_stats(db)
    groups = await list_groups(db)
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"stats": stats, "groups": groups},
    )

