#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_common.sh"

LOCK_FILE="${APP_DIR}/run/online_update.lock"
UPDATE_LOG="${APP_DIR}/logs/online_update.log"

ensure_runtime_dirs
cd "${APP_DIR}"

if command -v flock >/dev/null 2>&1; then
  exec 9>"${LOCK_FILE}"
  flock -n 9 || {
    echo "[miyin] update already running"
    exit 0
  }
fi

{
  echo "[miyin] online update start: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  git fetch origin "${BRANCH}"
  git checkout "${BRANCH}"
  git pull --ff-only origin "${BRANCH}"

  "${VENV_DIR}/bin/pip" install -r "${APP_DIR}/requirements.txt"

  stop_app_nohup
  start_app_nohup
  echo "[miyin] online update done: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
} >> "${UPDATE_LOG}" 2>&1

