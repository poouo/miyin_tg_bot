import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


REPO_URL = "https://github.com/poouo/miyin_tg_bot.git"
VERSION_FILE_NAME = "VERSION"
VERSION_PATTERN = re.compile(r"^[vV]?(\d+)\.(\d+)\.(\d+)$")


def _run(cmd: list[str], cwd: Path) -> tuple[bool, str]:
    try:
        result = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, check=True)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as exc:
        return False, (exc.stderr or exc.stdout or str(exc)).strip()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_version(version: str) -> str:
    return version.strip().replace("\r", "").replace("\n", "")


def _parse_version(version: str) -> tuple[int, int, int] | None:
    match = VERSION_PATTERN.match(_normalize_version(version))
    if not match:
        return None
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def _compare_versions(local_version: str, remote_version: str) -> int | None:
    left = _parse_version(local_version)
    right = _parse_version(remote_version)
    if left is None or right is None:
        return None
    if left < right:
        return -1
    if left > right:
        return 1
    return 0


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _online_status_file(repo: Path) -> Path:
    return repo / "data" / "online_update_status.json"


def _read_json_file(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_json_file(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _get_current_branch(repo: Path) -> str:
    ok, branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo)
    if ok and branch:
        return branch
    return "main"


def _read_local_version(repo: Path) -> tuple[bool, str]:
    version_file = repo / VERSION_FILE_NAME
    if not version_file.exists():
        return False, f"{VERSION_FILE_NAME} not found"
    return True, _normalize_version(version_file.read_text(encoding="utf-8"))


def _read_remote_version(repo: Path, branch: str) -> tuple[bool, str]:
    ok, output = _run(["git", "show", f"origin/{branch}:{VERSION_FILE_NAME}"], repo)
    if not ok:
        return False, output
    return True, _normalize_version(output)


def check_update() -> dict:
    repo = get_repo_root()
    if not (repo / ".git").exists():
        return {
            "ok": False,
            "message": "Current directory is not a git repository.",
            "repo_url": REPO_URL,
        }

    branch = _get_current_branch(repo)
    ok_fetch, fetch_msg = _run(["git", "fetch", "origin", branch], repo)
    if not ok_fetch:
        return {"ok": False, "message": fetch_msg, "repo_url": REPO_URL, "branch": branch}

    ok_local, local_version = _read_local_version(repo)
    if not ok_local:
        return {"ok": False, "message": local_version, "repo_url": REPO_URL, "branch": branch}

    ok_remote, remote_version = _read_remote_version(repo, branch)
    if not ok_remote:
        return {
            "ok": False,
            "message": remote_version,
            "repo_url": REPO_URL,
            "branch": branch,
            "local_version": local_version,
        }

    compare = _compare_versions(local_version, remote_version)
    if compare is None:
        has_update = local_version != remote_version
    else:
        has_update = compare < 0

    return {
        "ok": True,
        "repo_url": REPO_URL,
        "branch": branch,
        "local_version": local_version,
        "remote_version": remote_version,
        "has_update": has_update,
        "message": "Update available." if has_update else "Already up to date.",
        "compare_mode": "version",
        "checked_at": _utc_now(),
    }


def trigger_online_update() -> dict:
    repo = get_repo_root()
    script = repo / "scripts" / "linux" / "local" / "online_update.sh"
    if not script.exists():
        return {"ok": False, "message": f"Update script not found: {script}"}

    status_file = _online_status_file(repo)
    current = _read_json_file(status_file) or {}
    if current.get("state") == "running":
        return {"ok": False, "message": "Update is already running."}

    _write_json_file(
        status_file,
        {
            "state": "running",
            "progress": 3,
            "message": "Update task started.",
            "updated_at": _utc_now(),
        },
    )

    process = subprocess.Popen(
        ["bash", str(script), "--from-api"],
        cwd=str(repo),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return {"ok": True, "pid": process.pid, "message": "Online update started."}


def get_online_update_status() -> dict:
    repo = get_repo_root()
    status_file = _online_status_file(repo)
    data = _read_json_file(status_file)
    if data is None:
        return {
            "ok": True,
            "state": "idle",
            "progress": 0,
            "message": "No active update task.",
            "updated_at": _utc_now(),
        }
    return {"ok": True, **data}


def read_background_status() -> dict:
    repo = get_repo_root()
    status_file = repo / "data" / "update_status.json"
    if not status_file.exists():
        return {
            "ok": False,
            "message": "Background check status not found. Run local install script first.",
            "status_file": str(status_file),
        }
    data = _read_json_file(status_file)
    if data is None:
        return {"ok": False, "message": "Failed to parse background status file.", "status_file": str(status_file)}
    return {"ok": True, "data": data}

