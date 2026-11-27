import json
import os
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import quote
from urllib.request import urlopen

import httpx

if sys.platform == "linux":
    import fcntl


REPO_URL = "https://github.com/poouo/miyin_tg_bot.git"
RAW_REPO_URL = "https://raw.githubusercontent.com/poouo/miyin_tg_bot"
VERSION_FILE_NAME = "VERSION"
VERSION_PATTERN = re.compile(r"^[vV]?(\d+)\.(\d+)\.(\d+)$")
REVISION_PATTERN = re.compile(r"^[0-9a-f]{40}$")
IMAGE_REPOSITORY = "poouo/miyin_tg_bot"
REGISTRY = "https://ghcr.io"
MANIFEST_TYPES = ", ".join((
    "application/vnd.oci.image.index.v1+json",
    "application/vnd.docker.distribution.manifest.list.v2+json",
    "application/vnd.oci.image.manifest.v1+json",
    "application/vnd.docker.distribution.manifest.v2+json",
))
DIGEST_PATTERN = re.compile(r"sha256:[0-9a-f]{64}")


def _run(cmd: list[str], cwd: Path) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, encoding="utf-8", errors="replace", check=True,
            timeout=20, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as exc:
        return False, (exc.stderr or exc.stdout or str(exc)).strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)


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


def _online_lock_file(repo: Path) -> Path:
    return repo / "run" / "online_update.lock"


def _read_json_file(path: Path) -> dict | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else None
    except (OSError, ValueError):
        return None


def _write_json_file(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False)
    tmp_path = Path(tmp.name)
    try:
        with tmp:
            json.dump(payload, tmp, ensure_ascii=False)
        tmp_path.replace(path)
    finally:
        tmp_path.unlink(missing_ok=True)


def get_update_deployment() -> dict:
    docker = (
        os.getenv("MIYIN_DEPLOYMENT") == "docker"
        or Path("/.dockerenv").exists()
        or Path("/run/.containerenv").exists()
    )
    repo = get_repo_root()
    return {
        "mode": "docker" if docker else "local",
        "docker_source": os.getenv("MIYIN_DOCKER_SOURCE", ""),
        "can_online_update": bool(
            not docker
            and sys.platform == "linux"
            and (repo / ".git").exists()
            and shutil.which("bash")
        ),
    }


def _read_local_version(repo: Path) -> str:
    try:
        return _normalize_version((repo / VERSION_FILE_NAME).read_text(encoding="utf-8"))
    except (OSError, UnicodeError):
        return ""


def _latest_image_revision() -> str:
    machine = platform.machine().lower()
    architecture = {"x86_64": "amd64", "aarch64": "arm64"}.get(machine, machine)
    prefix = f"/v2/{IMAGE_REPOSITORY}"
    with httpx.Client(base_url=REGISTRY, timeout=10.0) as client:
        token = client.get("/token", params={
            "service": "ghcr.io", "scope": f"repository:{IMAGE_REPOSITORY}:pull",
        }).raise_for_status().json()["token"]
        client.headers["Authorization"] = f"Bearer {token}"

        def manifest(ref: str) -> dict:
            return client.get(f"{prefix}/manifests/{ref}", headers={
                "Accept": MANIFEST_TYPES,
            }).raise_for_status().json()

        image = manifest("latest")
        if "manifests" in image:
            digest = next(
                (
                    item["digest"] for item in image["manifests"]
                    if item.get("platform", {}).get("os") == "linux"
                    and item.get("platform", {}).get("architecture") == architecture
                ),
                "",
            )
            if not DIGEST_PATTERN.fullmatch(digest):
                raise ValueError(f"No published image for linux/{architecture}")
            image = manifest(digest)
        digest = image["config"]["digest"]
        if not DIGEST_PATTERN.fullmatch(digest):
            raise ValueError("Invalid image configuration digest")
        config = client.get(f"{prefix}/blobs/{digest}", follow_redirects=True).raise_for_status().json()["config"]
        revision = (config.get("Labels") or {}).get("org.opencontainers.image.revision", "")
        if not REVISION_PATTERN.fullmatch(revision):
            raise ValueError("Published image is missing its build revision")
        return revision


def _check_docker_update(repo: Path, local_version: str) -> dict:
    branch = os.getenv("MIYIN_BUILD_BRANCH", "").strip() or "main"
    local_revision = os.getenv("MIYIN_BUILD_REVISION", "").strip().lower()
    if os.getenv("MIYIN_DOCKER_SOURCE") == "image":
        if not REVISION_PATTERN.fullmatch(local_revision):
            return {"ok": False, "message": "Installed image is missing its build revision."}
        try:
            remote_revision = _latest_image_revision()
        except (httpx.HTTPError, ValueError, TypeError, KeyError) as exc:
            return {"ok": False, "message": f"Could not check the published Docker image: {exc}"}
        return {
            "ok": True, "branch": branch, "compare_mode": "image", "local_revision": local_revision,
            "remote_revision": remote_revision, "has_update": remote_revision != local_revision,
        }
    if REVISION_PATTERN.fullmatch(local_revision):
        ok, output = _run(["git", "ls-remote", "--exit-code", REPO_URL, f"refs/heads/{branch}"], repo)
        remote_revision = output.partition("\t")[0] if ok else ""
        if not REVISION_PATTERN.fullmatch(remote_revision):
            return {"ok": False, "message": output or "GitHub did not return a revision."}
        return {
            "ok": True, "branch": branch, "compare_mode": "revision", "local_revision": local_revision,
            "remote_revision": remote_revision, "has_update": remote_revision != local_revision,
        }

    try:
        with urlopen(f"{RAW_REPO_URL}/{quote(branch, safe='')}/{VERSION_FILE_NAME}", timeout=15) as response:
            remote_version = _normalize_version(response.read(128).decode("utf-8"))
    except (OSError, UnicodeError) as exc:
        return {"ok": False, "message": str(exc)}
    compare = _compare_versions(local_version, remote_version)
    if compare is None:
        return {"ok": False, "message": "Unable to compare the current and GitHub VERSION files."}
    return {
        "ok": True, "branch": branch, "compare_mode": "version",
        "remote_version": remote_version, "has_update": compare < 0,
    }


def _check_git_update(repo: Path) -> dict:
    ok, branch = _run(["git", "symbolic-ref", "--short", "HEAD"], repo)
    if not ok:
        return {"ok": False, "message": branch}
    remote_ref = f"refs/remotes/origin/{branch}"
    ok, output = _run(["git", "fetch", "origin", f"+refs/heads/{branch}:{remote_ref}"], repo)
    if not ok:
        return {"ok": False, "message": output, "branch": branch}
    ok, output = _run(["git", "rev-list", "--left-right", "--count", f"HEAD...{remote_ref}"], repo)
    if not ok:
        return {"ok": False, "message": output, "branch": branch}
    ahead, behind = map(int, output.split())
    ok, remote_version = _run(["git", "show", f"{remote_ref}:{VERSION_FILE_NAME}"], repo)
    return {
        "ok": True, "branch": branch, "compare_mode": "commits", "has_update": behind > 0,
        "diverged": ahead > 0 and behind > 0, "remote_version": _normalize_version(remote_version) if ok else "",
    }


def check_update() -> dict:
    repo = get_repo_root()
    deployment = get_update_deployment()
    local_version = _read_local_version(repo)
    result = (
        _check_docker_update(repo, local_version)
        if deployment["mode"] == "docker"
        else _check_git_update(repo)
    )
    if result["ok"]:
        result["message"] = "Update available." if result["has_update"] else "Already up to date."
    return {**result, **deployment, "repo_url": REPO_URL, "local_version": local_version, "checked_at": _utc_now()}


def trigger_online_update() -> dict:
    deployment = get_update_deployment()
    if not deployment["can_online_update"]:
        code = "update_docker_only" if deployment["mode"] == "docker" else "update_online_unavailable"
        return {"ok": False, "code": code, "message": "Online update is unavailable for this deployment."}

    repo = get_repo_root()
    script = repo / "scripts" / "linux" / "local" / "online_update.sh"
    if not script.exists():
        return {"ok": False, "message": f"Update script not found: {script}"}

    status_file = _online_status_file(repo)
    lock_path = _online_lock_file(repo)
    try:
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        with lock_path.open("a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return {"ok": False, "code": "update_already_running", "message": "Update is already running."}
            try:
                log_file = repo / "logs" / "online_update.log"
                log_file.parent.mkdir(parents=True, exist_ok=True)
                _write_json_file(status_file, {
                    "state": "running", "progress": 3, "code": "update_starting",
                    "message": "Update task started.", "updated_at": _utc_now(),
                })
                with log_file.open("ab") as log:
                    process = subprocess.Popen(
                        ["bash", str(script), "--from-api", str(lock.fileno())],
                        cwd=repo,
                        env={**os.environ, "APP_DIR": str(repo)},
                        pass_fds=(lock.fileno(),),
                        stdin=subprocess.DEVNULL,
                        stdout=log,
                        stderr=subprocess.STDOUT,
                        start_new_session=True,
                    )
            except OSError as exc:
                _write_json_file(status_file, {
                    "state": "failed", "progress": 0, "code": "update_start_failed",
                    "message": str(exc), "updated_at": _utc_now(),
                })
                return {"ok": False, "code": "update_start_failed", "message": str(exc)}
    except OSError as exc:
        return {"ok": False, "code": "update_start_failed", "message": str(exc)}
    return {"ok": True, "pid": process.pid, "message": "Online update started."}


def get_online_update_status() -> dict:
    if not get_update_deployment()["can_online_update"]:
        return {"ok": True, "state": "idle", "progress": 0}

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
    lock_path = _online_lock_file(repo)
    if data.get("state") == "running":
        try:
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            with lock_path.open("a") as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                # A task may have finished after the first read.
                data = _read_json_file(status_file) or data
                if data.get("state") == "running":
                    data = {
                        **data, "state": "failed", "code": "update_interrupted",
                        "message": "The update process stopped before reporting a result.", "updated_at": _utc_now(),
                    }
                    _write_json_file(status_file, data)
        except BlockingIOError:
            pass
        except OSError as exc:
            return {"ok": False, "message": str(exc)}
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


def write_background_status() -> None:
    result = check_update()
    _write_json_file(
        get_repo_root() / "data" / "update_status.json",
        {"has_update": False, **result, "status": "ok" if result["ok"] else "error"},
    )

