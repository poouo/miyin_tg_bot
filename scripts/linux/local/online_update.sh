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

LOCK_FILE="${APP_DIR}/run/online_update.lock"
STATUS_FILE="${APP_DIR}/data/online_update_status.json"
CURRENT_PROGRESS=0

ensure_runtime_dirs
cd "${APP_DIR}"

write_status() {
  local state="$1"
  local progress="$2"
  local code="$3"
  local message="$4"
  local tmp
  CURRENT_PROGRESS="${progress}"
  tmp="$(mktemp "${STATUS_FILE}.XXXXXX")"
  cat > "${tmp}" <<EOF
{
  "state": "${state}",
  "progress": ${progress},
  "code": "${code}",
  "message": "${message}",
  "updated_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
  mv -f -- "${tmp}" "${STATUS_FILE}"
}

on_error() {
  write_status "failed" "${CURRENT_PROGRESS}" "update_failed_retry" "Update failed."
}

if [[ "${1:-}" == "--from-api" ]]; then
  lock_fd="${2:?missing inherited update lock}"
else
  exec {lock_fd}>>"${LOCK_FILE}"
  if ! flock -n "${lock_fd}"; then
    echo "An update is already running."
    exit 1
  fi
fi

trap on_error ERR

write_status "running" 8 "update_preparing" "Preparing update..."
branch="$(git symbolic-ref --short HEAD)"
changes="$(git status --porcelain --untracked-files=no)"
if [[ -n "${changes}" ]]; then
  write_status "failed" "${CURRENT_PROGRESS}" "update_dirty_checkout" "The local checkout has uncommitted changes."
  git status --short
  exit 1
fi
remote_ref="refs/remotes/origin/${branch}"
GIT_TERMINAL_PROMPT=0 git fetch origin "+refs/heads/${branch}:${remote_ref}"
if ! git merge-base --is-ancestor HEAD "${remote_ref}"; then
  write_status "failed" "${CURRENT_PROGRESS}" "update_diverged" "The current branch cannot be fast-forwarded."
  exit 1
fi
git merge --ff-only --no-overwrite-ignore "${remote_ref}"

write_status "running" 45 "update_installing" "Installing dependencies..."
"${VENV_DIR}/bin/pip" install -r "${APP_DIR}/requirements.txt"

write_status "running" 82 "update_restarting" "Restarting service..."
stop_app_nohup
(
  exec {lock_fd}>&-
  start_app_nohup
)

write_status "success" 100 "update_success" "Update completed."
