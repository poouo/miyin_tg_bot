#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/miyin_tg_bot}"
PURGE_DATA="${PURGE_DATA:-false}"

if [[ ! -d "${APP_DIR}" ]]; then
  echo "目录不存在: ${APP_DIR}"
  exit 0
fi

cd "${APP_DIR}"
if command -v docker >/dev/null 2>&1; then
  sudo docker compose down --remove-orphans || true
fi

if [[ "${PURGE_DATA}" == "true" ]]; then
  sudo rm -rf "${APP_DIR}/data" "${APP_DIR}/logs"
  echo "[miyin] 数据目录已删除"
fi

echo "[miyin] uninstall done (代码目录保留在 ${APP_DIR})"

