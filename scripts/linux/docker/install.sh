#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/poouo/miyin_tg_bot.git"
APP_DIR="${APP_DIR:-/opt/miyin_tg_bot}"
BRANCH="${BRANCH:-main}"

echo "[miyin] docker install start"

run_privileged() {
  if [[ "${EUID}" -eq 0 ]]; then
    "$@"
  else
    sudo "$@"
  fi
}

if ! command -v docker >/dev/null 2>&1; then
  echo "docker not found, please install Docker first"
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "docker compose is unavailable"
  exit 1
fi

if [[ ! -d "${APP_DIR}/.git" ]]; then
  run_privileged mkdir -p "${APP_DIR}"
  run_privileged git clone -b "${BRANCH}" "${REPO_URL}" "${APP_DIR}"
else
  cd "${APP_DIR}"
  run_privileged git fetch origin "${BRANCH}"
  run_privileged git checkout "${BRANCH}"
  run_privileged git pull --ff-only origin "${BRANCH}"
fi

cd "${APP_DIR}"

if [[ ! -f "docker-compose.yml" ]]; then
  echo "[miyin] docker-compose.yml missing in ${APP_DIR}, verify APP_DIR or repository content"
  exit 1
fi

if [[ ! -f ".env.example" ]]; then
  echo "[miyin] .env.example missing, trying to fetch template from GitHub..."
  ENV_EXAMPLE_URL="https://raw.githubusercontent.com/poouo/miyin_tg_bot/${BRANCH}/.env.example"
  if command -v curl >/dev/null 2>&1; then
    run_privileged bash -c "curl -fsSL '${ENV_EXAMPLE_URL}' > '${APP_DIR}/.env.example'"
  elif command -v wget >/dev/null 2>&1; then
    run_privileged bash -c "wget -qO- '${ENV_EXAMPLE_URL}' > '${APP_DIR}/.env.example'"
  else
    echo "curl or wget required to fetch .env.example"
    exit 1
  fi
fi

if [[ ! -f ".env" ]]; then
  run_privileged cp .env.example .env
  echo "[miyin] created .env, please edit Bot Token and DeepSeek Key"
fi

run_privileged mkdir -p data logs
run_privileged docker compose up -d --build
echo "[miyin] docker install done"
echo "[miyin] web: http://<server-ip>:9800"

