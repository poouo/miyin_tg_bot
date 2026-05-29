#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_common.sh"

CHECK_INTERVAL_SEC="${CHECK_INTERVAL_SEC:-600}"

ensure_runtime_dirs
cd "${APP_DIR}"

while true; do
  status="ok"
  message=""
  local_commit=""
  remote_commit=""
  has_update="false"
  checked_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

  if [[ ! -d ".git" ]]; then
    status="error"
    message="not a git repo"
  else
    if git fetch origin "${BRANCH}" >/dev/null 2>&1; then
      local_commit="$(git rev-parse HEAD 2>/dev/null || true)"
      remote_commit="$(git rev-parse "origin/${BRANCH}" 2>/dev/null || true)"
      if [[ -n "${local_commit}" && -n "${remote_commit}" && "${local_commit}" != "${remote_commit}" ]]; then
        has_update="true"
      fi
    else
      status="error"
      message="git fetch failed"
    fi
  fi

  cat > "${UPDATE_STATUS_FILE}" <<EOF
{
  "status": "${status}",
  "message": "${message}",
  "branch": "${BRANCH}",
  "local_commit": "${local_commit}",
  "remote_commit": "${remote_commit}",
  "has_update": ${has_update},
  "checked_at": "${checked_at}"
}
EOF

  sleep "${CHECK_INTERVAL_SEC}"
done

