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
VERSION_FILE="${APP_DIR}/VERSION"

version_key() {
  local v="${1#V}"
  v="${v#v}"
  if [[ "${v}" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
    printf "%06d%06d%06d" "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}" "${BASH_REMATCH[3]}"
    return 0
  fi
  return 1
}

ensure_runtime_dirs
cd "${APP_DIR}"

while true; do
  status="ok"
  message=""
  local_version=""
  remote_version=""
  has_update="false"
  checked_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

  if [[ ! -d ".git" ]]; then
    status="error"
    message="not a git repo"
  else
    if git fetch origin "${BRANCH}" >/dev/null 2>&1; then
      if [[ -f "${VERSION_FILE}" ]]; then
        local_version="$(tr -d '\r\n' < "${VERSION_FILE}")"
      else
        status="error"
        message="VERSION file not found"
      fi

      remote_version="$(git show "origin/${BRANCH}:VERSION" 2>/dev/null | tr -d '\r\n' || true)"

      if [[ "${status}" == "ok" && -n "${local_version}" && -n "${remote_version}" ]]; then
        if local_key="$(version_key "${local_version}")" && remote_key="$(version_key "${remote_version}")"; then
          if [[ "${remote_key}" > "${local_key}" ]]; then
            has_update="true"
          fi
        elif [[ "${local_version}" != "${remote_version}" ]]; then
          has_update="true"
        fi
      elif [[ "${status}" == "ok" && -z "${remote_version}" ]]; then
        status="error"
        message="failed to read remote VERSION"
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
  "local_version": "${local_version}",
  "remote_version": "${remote_version}",
  "has_update": ${has_update},
  "compare_mode": "version",
  "checked_at": "${checked_at}"
}
EOF

  sleep "${CHECK_INTERVAL_SEC}"
done
