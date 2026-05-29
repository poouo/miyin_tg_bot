#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_common.sh"

LOCK_FILE="${APP_DIR}/run/online_update.lock"
STATUS_FILE="${APP_DIR}/data/online_update_status.json"
CURRENT_PROGRESS=0

ensure_runtime_dirs
cd "${APP_DIR}"

write_status() {
  local state="$1"
  local progress="$2"
  local message="$3"
  CURRENT_PROGRESS="${progress}"
  cat > "${STATUS_FILE}" <<EOF
{
  "state": "${state}",
  "progress": ${progress},
  "message": "${message}",
  "updated_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
}

on_error() {
  write_status "failed" "${CURRENT_PROGRESS}" "Update failed."
}

trap on_error ERR

if command -v flock >/dev/null 2>&1; then
  exec 9>"${LOCK_FILE}"
  flock -n 9 || {
    write_status "running" 10 "Update already running."
    exit 0
  }
fi

write_status "running" 8 "Preparing update..."
git fetch origin "${BRANCH}"
git checkout "${BRANCH}"
git pull --ff-only origin "${BRANCH}"

write_status "running" 45 "Installing dependencies..."
"${VENV_DIR}/bin/pip" install -r "${APP_DIR}/requirements.txt"

write_status "running" 82 "Restarting service..."
stop_app_nohup
start_app_nohup

write_status "success" 100 "Update completed."

