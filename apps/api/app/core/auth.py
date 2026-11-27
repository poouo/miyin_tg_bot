import base64
import hashlib
import hmac
import json
import time
from typing import Any

from fastapi import HTTPException, Request, Response, status

from apps.api.app.services.admin_password_service import admin_session_material
from packages.shared.shared.config.settings import settings

ADMIN_COOKIE_NAME = "miyin_admin_token"


def _sign(payload: bytes) -> bytes:
    return hmac.new(
        settings.web_auth_secret.encode(),
        b"admin-session-v2\0" + admin_session_material() + b"\0" + payload,
        hashlib.sha256,
    ).digest()


def set_admin_cookie(request: Request, response: Response) -> None:
    response.set_cookie(
        key=ADMIN_COOKIE_NAME,
        value=create_admin_token(),
        max_age=settings.web_token_expire_days * 24 * 60 * 60,
        httponly=True,
        samesite="lax",
        secure=request.url.scheme == "https",
    )


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode())


def create_admin_token() -> str:
    now = int(time.time())
    payload = {
        "sub": "admin",
        "iat": now,
        "exp": now + settings.web_token_expire_days * 24 * 60 * 60,
    }
    payload_raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode()
    sig = _sign(payload_raw)
    return f"{_b64url_encode(payload_raw)}.{_b64url_encode(sig)}"


def verify_admin_token(token: str) -> bool:
    try:
        payload_part, sig_part = token.split(".", 1)
        payload_raw = _b64url_decode(payload_part)
        provided_sig = _b64url_decode(sig_part)
        expected_sig = _sign(payload_raw)
        if not hmac.compare_digest(provided_sig, expected_sig):
            return False
        payload: dict[str, Any] = json.loads(payload_raw.decode())
        exp = int(payload.get("exp", 0))
        if exp <= int(time.time()):
            return False
        return payload.get("sub") == "admin"
    except Exception:
        return False


def is_admin_authenticated(request: Request) -> bool:
    token = request.cookies.get(ADMIN_COOKIE_NAME, "")
    if not token:
        return False
    return verify_admin_token(token)


def get_client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


async def require_admin_api(request: Request) -> None:
    if is_admin_authenticated(request):
        return
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

