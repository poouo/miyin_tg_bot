import json

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.auth import ADMIN_COOKIE_NAME, create_admin_token, get_client_ip, is_admin_authenticated
from apps.api.app.core.db import get_db
from apps.api.app.core.i18n import get_translations, tr
from apps.api.app.services.admin_password_service import verify_admin_password
from apps.api.app.services.group_service import list_groups
from apps.api.app.services.security_service import (
    check_login_allowed,
    clear_login_attempt,
    get_or_create_security_config,
    register_failed_login,
)
from apps.api.app.services.stats_service import dashboard_stats
from apps.api.app.services.web_language_service import read_web_language
from packages.shared.shared.config.settings import settings

router = APIRouter(tags=["admin"])
templates = Jinja2Templates(directory="apps/api/app/templates")


def _build_i18n_context(lang: str) -> dict:
    t = get_translations(lang)
    return {
        "lang": lang,
        "t": t,
        "t_json": json.dumps(t, ensure_ascii=False),
    }


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> HTMLResponse | RedirectResponse:
    if is_admin_authenticated(request):
        return RedirectResponse(url="/", status_code=303)
    lang = read_web_language()
    context = {"error": "", **_build_i18n_context(lang)}
    return templates.TemplateResponse(request=request, name="login.html", context=context)


@router.post("/auth/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse | RedirectResponse:
    if is_admin_authenticated(request):
        return RedirectResponse(url="/", status_code=303)

    lang = read_web_language()
    ip = get_client_ip(request)
    allowed, wait_minutes = await check_login_allowed(db, ip)
    if not allowed:
        error = tr(lang, "login_error_too_many_attempts", minutes=wait_minutes)
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": error, **_build_i18n_context(lang)},
        )

    if not verify_admin_password(password):
        await register_failed_login(db, ip)
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": tr(lang, "login_error_password"), **_build_i18n_context(lang)},
        )

    await clear_login_attempt(db, ip)
    token = create_admin_token()
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key=ADMIN_COOKIE_NAME,
        value=token,
        max_age=settings.web_token_expire_days * 24 * 60 * 60,
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return response


@router.post("/auth/logout")
async def logout() -> RedirectResponse:
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(ADMIN_COOKIE_NAME)
    return response


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: AsyncSession = Depends(get_db)) -> HTMLResponse | RedirectResponse:
    if not is_admin_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)

    stats = await dashboard_stats(db)
    groups = await list_groups(db)
    security = await get_or_create_security_config(db)
    lang = read_web_language()
    context = {"stats": stats, "groups": groups, "security": security, **_build_i18n_context(lang)}
    return templates.TemplateResponse(request=request, name="dashboard.html", context=context)
