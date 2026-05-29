#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_common.sh"

if [[ ! -d "${APP_DIR}/.git" ]]; then
  echo "未找到项目目录 ${APP_DIR}，请先执行 install.sh"
  exit 1
fi

bash "${SCRIPT_DIR}/online_update.sh"

