#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/miyin_tg_bot}"
PURGE_DATA="${PURGE_DATA:-false}"

run_privileged() {
  if [[ "${EUID}" -eq 0 ]]; then
    "$@"
  else
    sudo "$@"
  fi
}

if [[ ! -d "${APP_DIR}" ]]; then
  echo "directory not found: ${APP_DIR}"
  exit 0
fi

cd "${APP_DIR}"
if command -v docker >/dev/null 2>&1; then
  run_privileged docker compose down --remove-orphans || true
fi

if [[ "${PURGE_DATA}" == "true" ]]; then
  run_privileged rm -rf "${APP_DIR}/data" "${APP_DIR}/logs"
  echo "[miyin] data directories removed"
fi

echo "[miyin] uninstall done (code directory kept at ${APP_DIR})"

