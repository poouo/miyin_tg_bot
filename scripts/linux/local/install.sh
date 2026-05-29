#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_common.sh"

echo "[miyin] local install start"

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "未找到 ${PYTHON_BIN}，请先安装 Python3"
  exit 1
fi

ensure_repo
ensure_runtime_dirs
cd "${APP_DIR}"

if [[ ! -d "${VENV_DIR}" ]]; then
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

"${VENV_DIR}/bin/pip" install --upgrade pip
"${VENV_DIR}/bin/pip" install -r "${APP_DIR}/requirements.txt"

if [[ ! -f "${APP_DIR}/.env" ]]; then
  cp "${APP_DIR}/.env.example" "${APP_DIR}/.env"
  echo "[miyin] 已生成 .env，请先配置 BOT Token 和 DeepSeek API Key"
fi

start_app_nohup
start_update_checker

echo "[miyin] local install done"
echo "[miyin] web: http://<server-ip>:8080"
echo "[miyin] update status file: ${UPDATE_STATUS_FILE}"
