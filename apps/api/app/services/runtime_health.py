from datetime import datetime, timedelta, timezone
from hashlib import sha256

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.services.runtime_config_service import AICredentials

_bot = {"state": "starting", "last_success": None}
_ai: dict[str, tuple[str, datetime, bool]] = {}


def record_bot(state: str) -> None:
    _bot["state"] = state
    if state == "online":
        _bot["last_success"] = datetime.now(timezone.utc)
    elif state in {"starting", "not_configured"}:
        _bot["last_success"] = None


def _ai_key(credentials: AICredentials) -> str:
    value = "\0".join((credentials.provider, credentials.base_url, credentials.model, credentials.api_key))
    return sha256(value.encode()).hexdigest()


def record_ai(credentials: AICredentials, success: bool) -> None:
    _ai[credentials.provider] = (_ai_key(credentials), datetime.now(timezone.utc), success)


def bot_health() -> dict:
    state = _bot["state"]
    last = _bot["last_success"]
    if state == "online" and last < datetime.now(timezone.utc) - timedelta(minutes=2):
        state = "error"
    return {"state": state, "last_success": last.isoformat() if last else None}


def ai_health(credentials: AICredentials) -> dict:
    if not all((credentials.api_key, credentials.base_url, credentials.model)):
        return {"state": "not_configured"}
    last = _ai.get(credentials.provider)
    if not last or last[0] != _ai_key(credentials):
        return {"state": "untested"}
    _, checked_at, success = last
    return {"state": "online" if success else "error", "checked_at": checked_at.isoformat()}


async def database_healthy(db: AsyncSession) -> bool:
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        return False
    return True
