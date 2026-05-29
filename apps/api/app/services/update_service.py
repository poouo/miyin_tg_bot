import subprocess
from datetime import datetime, timezone
from pathlib import Path
import json


REPO_URL = "https://github.com/poouo/miyin_tg_bot.git"


def _run(cmd: list[str], cwd: Path) -> tuple[bool, str]:
    try:
        result = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, check=True)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as exc:
        return False, (exc.stderr or exc.stdout or str(exc)).strip()


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def check_update() -> dict:
    repo = get_repo_root()
    if not (repo / ".git").exists():
        return {
            "ok": False,
            "message": "当前目录不是 git 仓库，无法检查更新。",
            "repo_url": REPO_URL,
        }

    ok_local, local = _run(["git", "rev-parse", "HEAD"], repo)
    if not ok_local:
        return {"ok": False, "message": local, "repo_url": REPO_URL}

    ok_remote, remote = _run(["git", "ls-remote", "origin", "HEAD"], repo)
    if not ok_remote:
        return {"ok": False, "message": remote, "repo_url": REPO_URL, "local_commit": local}

    remote_commit = remote.split()[0] if remote else ""
    return {
        "ok": True,
        "repo_url": REPO_URL,
        "local_commit": local,
        "remote_commit": remote_commit,
        "has_update": bool(remote_commit and remote_commit != local),
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def trigger_online_update() -> dict:
    repo = get_repo_root()
    script = repo / "scripts" / "linux" / "local" / "online_update.sh"
    if not script.exists():
        return {"ok": False, "message": f"更新脚本不存在: {script}"}

    # 后台触发更新任务，避免阻塞 Web 请求。
    process = subprocess.Popen(
        ["bash", str(script), "--from-api"],
        cwd=str(repo),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return {"ok": True, "pid": process.pid, "message": "在线更新任务已触发"}


def read_background_status() -> dict:
    repo = get_repo_root()
    status_file = repo / "data" / "update_status.json"
    if not status_file.exists():
        return {
            "ok": False,
            "message": "后台更新状态文件不存在，请先运行 scripts/linux/local/install.sh",
            "status_file": str(status_file),
        }
    try:
        return {"ok": True, "data": json.loads(status_file.read_text(encoding="utf-8"))}
    except Exception as exc:
        return {"ok": False, "message": f"读取状态失败: {exc}", "status_file": str(status_file)}
