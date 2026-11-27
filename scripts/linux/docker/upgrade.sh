#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/miyin_tg_bot}"

run_privileged() {
  if [[ "${EUID}" -eq 0 ]]; then
    "$@"
  else
    sudo "$@"
  fi
}

if [[ ! -e "${APP_DIR}/.git" ]]; then
  echo "project directory not found: ${APP_DIR}, run install.sh first"
  exit 1
fi

cd "${APP_DIR}"
branch="$(run_privileged git symbolic-ref --short HEAD)"
if [[ -n "${BRANCH:-}" && "${BRANCH}" != "${branch}" ]]; then
  echo "Check out ${BRANCH} before upgrading."
  exit 1
fi
run_privileged git pull --ff-only --no-rebase origin "${branch}"
revision="$(run_privileged git rev-parse HEAD)"
run_privileged env MIYIN_BUILD_REVISION="${revision}" MIYIN_BUILD_BRANCH="${branch}" docker compose up -d --build
echo "[miyin] docker upgrade done"
