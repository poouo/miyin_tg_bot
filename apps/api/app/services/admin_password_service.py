import hashlib
import hmac
import json
import secrets
from pathlib import Path

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
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def verify_admin_password(password: str) -> bool:
    payload = _read_password_payload()
    if payload is None:
        return hmac.compare_digest(password, settings.web_admin_password)

    salt_hex = payload.get("salt_hex", "")
    hash_hex = payload.get("hash_hex", "")
    if not salt_hex or not hash_hex:
        return hmac.compare_digest(password, settings.web_admin_password)

    current_hash = _hash_password(password, salt_hex)
    return hmac.compare_digest(current_hash, hash_hex)


def set_admin_password(new_password: str) -> None:
    salt_hex = secrets.token_hex(16)
    hash_hex = _hash_password(new_password, salt_hex)
    payload = {"salt_hex": salt_hex, "hash_hex": hash_hex}
    path = _password_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True), encoding="utf-8")

