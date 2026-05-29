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

write_default_env_example() {
  run_privileged tee "${APP_DIR}/.env.example" >/dev/null <<'EOF'
APP_ENV=prod
LOG_LEVEL=INFO
PROJECT_NAME=miyin_tg_bot

DATABASE_URL=sqlite+aiosqlite:///./data/miyin.db

WEB_HOST=0.0.0.0
WEB_PORT=9800
WEB_ADMIN_PASSWORD=admin
WEB_AUTH_SECRET=change_me_to_a_long_random_string
WEB_TOKEN_EXPIRE_DAYS=10
EOF
}

ensure_env_example() {
  if [[ -f "${APP_DIR}/.env.example" ]]; then
    return 0
  fi

  echo "[miyin] .env.example missing, trying to fetch template from GitHub..."
  local urls=(
    "https://raw.githubusercontent.com/poouo/miyin_tg_bot/${BRANCH}/.env.example"
    "https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/.env.example"
  )
  local url

  for url in "${urls[@]}"; do
    if command -v curl >/dev/null 2>&1; then
      if run_privileged curl -fsSL "${url}" -o "${APP_DIR}/.env.example"; then
        echo "[miyin] .env.example downloaded from ${url}"
        return 0
      fi
    elif command -v wget >/dev/null 2>&1; then
      if run_privileged wget -qO "${APP_DIR}/.env.example" "${url}"; then
        echo "[miyin] .env.example downloaded from ${url}"
        return 0
      fi
    fi
  done

  echo "[miyin] failed to download .env.example, using built-in template"
  write_default_env_example
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
  run_privileged git checkout -B "${BRANCH}" "origin/${BRANCH}"
  run_privileged git reset --hard "origin/${BRANCH}"
fi

cd "${APP_DIR}"

if [[ ! -f "docker-compose.yml" ]]; then
  echo "[miyin] docker-compose.yml missing in ${APP_DIR}, verify APP_DIR or repository content"
  exit 1
fi

ensure_env_example

if [[ ! -f ".env" ]]; then
  run_privileged cp .env.example .env
  echo "[miyin] created .env, then set runtime bot/deepseek config in web admin"
fi

run_privileged mkdir -p data logs
run_privileged docker compose up -d --build
echo "[miyin] docker install done"
echo "[miyin] web: http://<server-ip>:9800"
