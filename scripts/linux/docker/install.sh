#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/poouo/miyin_tg_bot.git"
APP_DIR="${APP_DIR:-/opt/miyin_tg_bot}"
BRANCH="${BRANCH:-main}"

echo "[miyin] docker install start"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker 未安装，请先安装 Docker"
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "docker compose 不可用，请升级 Docker"
  exit 1
fi

if [[ ! -d "${APP_DIR}/.git" ]]; then
  sudo mkdir -p "${APP_DIR}"
  sudo git clone -b "${BRANCH}" "${REPO_URL}" "${APP_DIR}"
else
  cd "${APP_DIR}"
  sudo git fetch origin "${BRANCH}"
  sudo git checkout "${BRANCH}"
  sudo git pull --ff-only origin "${BRANCH}"
fi

cd "${APP_DIR}"
if [[ ! -f .env ]]; then
  sudo cp .env.example .env
  echo "[miyin] 已生成 .env，请先编辑 Bot Token 和 DeepSeek Key"
fi

sudo mkdir -p data logs
sudo docker compose up -d --build
echo "[miyin] docker install done"
echo "[miyin] web: http://<server-ip>:9800"
