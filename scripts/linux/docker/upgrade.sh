#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/miyin_tg_bot}"
BRANCH="${BRANCH:-main}"

run_privileged() {
  if [[ "${EUID}" -eq 0 ]]; then
    "$@"
  else
    sudo "$@"
  fi
}

if [[ ! -d "${APP_DIR}/.git" ]]; then
  echo "project directory not found: ${APP_DIR}, run install.sh first"
  exit 1
fi

cd "${APP_DIR}"
run_privileged git fetch origin "${BRANCH}"
run_privileged git checkout -B "${BRANCH}" "origin/${BRANCH}"
run_privileged git reset --hard "origin/${BRANCH}"
run_privileged docker compose up -d --build
echo "[miyin] docker upgrade done"
