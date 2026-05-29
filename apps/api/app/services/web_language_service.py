import json
from pathlib import Path

from apps.api.app.core.i18n import DEFAULT_LANG, normalize_language


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _lang_file() -> Path:
    return _repo_root() / "data" / "web_language.json"


def read_web_language() -> str:
    path = _lang_file()
    if not path.exists():
        return DEFAULT_LANG
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return DEFAULT_LANG
    return normalize_language(payload.get("web_language"))


def write_web_language(lang: str) -> str:
    normalized = normalize_language(lang)
    path = _lang_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"web_language": normalized}, ensure_ascii=False), encoding="utf-8")
    return normalized

