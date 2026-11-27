#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export APP_DIR="${APP_DIR:-/opt/miyin_tg_bot}"

if [[ ! -e "${APP_DIR}/.git" ]]; then
  echo "未找到项目目录 ${APP_DIR}，请先执行 install.sh"
  exit 1
fi

if [[ -f "${SCRIPT_DIR}/online_update.sh" ]]; then
  exec bash "${SCRIPT_DIR}/online_update.sh"
fi

branch="${BRANCH:-main}"
url="https://raw.githubusercontent.com/poouo/miyin_tg_bot/${branch}/scripts/linux/local/online_update.sh"
script="$(mktemp)"
trap 'rm -f -- "$script"' EXIT
if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$url" -o "$script"
else
  wget -qO "$script" "$url"
fi
BRANCH="$branch" bash "$script"
