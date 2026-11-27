#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMON_PATH="${SCRIPT_DIR}/_common.sh"
if [[ -f "${COMMON_PATH}" ]]; then
  source "${COMMON_PATH}"
else
  BRANCH="${BRANCH:-main}"
  COMMON_URL="https://raw.githubusercontent.com/poouo/miyin_tg_bot/${BRANCH}/scripts/linux/local/_common.sh"
  if command -v curl >/dev/null 2>&1; then
    source <(curl -fsSL "${COMMON_URL}")
  elif command -v wget >/dev/null 2>&1; then
    source <(wget -qO- "${COMMON_URL}")
  else
    echo "curl or wget is required to load _common.sh"
    exit 1
  fi
fi

CHECK_INTERVAL_SEC="${CHECK_INTERVAL_SEC:-600}"

ensure_runtime_dirs
cd "${APP_DIR}"

while true; do
  "${VENV_DIR}/bin/python" -c 'from apps.api.app.services.update_service import write_background_status; write_background_status()' ||
    echo "Failed to write update status."
  sleep "${CHECK_INTERVAL_SEC}"
done
