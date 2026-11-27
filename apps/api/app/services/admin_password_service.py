import hashlib
import hmac
import json
import secrets
from pathlib import Path
from tempfile import NamedTemporaryFile

from packages.shared.shared.config.settings import settings


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _password_file() -> Path:
    return _repo_root() / "data" / "admin_password.json"


def _hash_password(password: str, salt_hex: str) -> str:
    salt = bytes.fromhex(salt_hex)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return digest.hex()


def _read_password_payload() -> dict | None:
    path = _password_file()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def admin_session_material() -> bytes:
    payload = _read_password_payload()
    if payload is None:
        return hashlib.sha256(settings.web_admin_password.encode()).digest()
    return f"{payload.get('salt_hex', '')}:{payload.get('hash_hex', '')}".encode()


def validate_admin_credentials() -> None:
    production = settings.app_env.strip().lower() in {"prod", "production"}
    loopback = settings.web_host.strip().lower() in {"127.0.0.1", "localhost", "::1"}
    if not production and loopback:
        return
    if len(settings.web_auth_secret.strip()) < 32 or settings.web_auth_secret == "change_me_to_a_long_random_string":
        raise RuntimeError("Set a unique WEB_AUTH_SECRET of at least 32 characters before starting production.")
    payload = _read_password_payload()
    if payload is None:
        if len(settings.web_admin_password.strip()) < 8:
            raise RuntimeError("Set a unique WEB_ADMIN_PASSWORD of at least 8 characters before starting production.")
    elif not payload.get("salt_hex") or not payload.get("hash_hex"):
        raise RuntimeError("The saved admin password record is invalid.")


def verify_admin_password(password: str) -> bool:
    payload = _read_password_payload()
    if payload is None:
        return hmac.compare_digest(password.encode("utf-8"), settings.web_admin_password.encode("utf-8"))

    salt_hex = payload.get("salt_hex", "")
    hash_hex = payload.get("hash_hex", "")
    if not isinstance(salt_hex, str) or not isinstance(hash_hex, str) or not salt_hex or not hash_hex:
        return False

    try:
        current_hash = _hash_password(password, salt_hex)
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(current_hash, hash_hex)


def set_admin_password(new_password: str) -> None:
    salt_hex = secrets.token_hex(16)
    hash_hex = _hash_password(new_password, salt_hex)
    payload = {"salt_hex": salt_hex, "hash_hex": hash_hex}
    path = _password_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    file = NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False)
    temporary = Path(file.name)
    try:
        with file:
            json.dump(payload, file, ensure_ascii=True)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)

