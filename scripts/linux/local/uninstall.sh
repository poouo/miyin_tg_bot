#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_common.sh"

PURGE_DATA="${PURGE_DATA:-false}"
PURGE_APP="${PURGE_APP:-false}"

stop_app_nohup
stop_update_checker

if [[ "${PURGE_DATA}" == "true" ]]; then
  rm -rf "${APP_DIR}/data" "${APP_DIR}/logs" "${APP_DIR}/run"
  echo "[miyin] 已删除运行数据"
fi

if [[ "${PURGE_APP}" == "true" ]]; then
  rm -rf "${APP_DIR}"
  echo "[miyin] 已删除项目目录 ${APP_DIR}"
else
  echo "[miyin] 已停止服务，代码目录保留在 ${APP_DIR}"
fi
