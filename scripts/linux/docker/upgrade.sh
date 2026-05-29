#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/miyin_tg_bot}"
BRANCH="${BRANCH:-main}"

if [[ ! -d "${APP_DIR}/.git" ]]; then
  echo "未找到项目目录 ${APP_DIR}，请先执行 install.sh"
  exit 1
fi

cd "${APP_DIR}"
sudo git fetch origin "${BRANCH}"
sudo git checkout "${BRANCH}"
sudo git pull --ff-only origin "${BRANCH}"
sudo docker compose up -d --build
echo "[miyin] docker upgrade done"

