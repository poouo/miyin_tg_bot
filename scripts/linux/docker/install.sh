#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${APP_DIR:-/opt/miyin_tg_bot}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
IMAGE="ghcr.io/poouo/miyin_tg_bot:${IMAGE_TAG}"
RAW_REPO="https://raw.githubusercontent.com/poouo/miyin_tg_bot/main"
MODE="${1:-}"
IMAGE_OVERRIDE="compose.miyin-image.yaml"
IMAGE_MARKER="# Managed by the Miyin Docker installer."

run_privileged() {
  if [[ "${EUID}" -eq 0 ]]; then
    "$@"
  else
    sudo "$@"
  fi
}

download() {
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$1" -o "$2"
  else
    wget -qO "$2" "$1"
  fi
}

if [[ ! "${IMAGE_TAG}" =~ ^[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}$ ]]; then
  echo "[miyin] invalid IMAGE_TAG" >&2
  exit 1
fi
if ! run_privileged docker compose version >/dev/null 2>&1; then
  echo "[miyin] Docker with the Compose plugin is required" >&2
  exit 1
fi
if [[ "${MODE}" == "--upgrade" && ! -d "${APP_DIR}" ]]; then
  echo "[miyin] deployment directory missing: ${APP_DIR}" >&2
  exit 1
fi

run_privileged mkdir -p "${APP_DIR}"
cd "${APP_DIR}"
APP_DIR="$(pwd -P)"
work="$(mktemp -d)"
override_tmp=""
cleanup() {
  if [[ -n "${override_tmp}" ]]; then
    run_privileged rm -f -- "${override_tmp}"
  fi
  rm -f -- "$work/init_env.sh" "$work/env.example"
  rmdir -- "$work"
}
trap cleanup EXIT

compose_args=()
if [[ -n "${COMPOSE_FILE:-}" ]]; then
  IFS="${COMPOSE_PATH_SEPARATOR:-:}" read -r -a files <<< "${COMPOSE_FILE}"
  for file in "${files[@]}"; do
    compose_args+=(-f "${file}")
  done
else
  for file in compose.yaml compose.yml docker-compose.yml docker-compose.yaml; do
    if [[ -f "${file}" ]]; then
      compose_args+=(-f "${file}")
      break
    fi
  done

  if [[ "${#compose_args[@]}" -eq 0 ]]; then
    if [[ "${MODE}" == "--upgrade" ]]; then
      echo "[miyin] no Compose deployment found in ${APP_DIR}" >&2
      exit 1
    fi
    run_privileged tee compose.yaml >/dev/null <<'EOF'
services:
  app:
    image: ghcr.io/poouo/miyin_tg_bot:latest
    container_name: miyin-tg-bot
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./data:/app/data
    ports:
      - "${WEB_PORT:-9800}:${WEB_PORT:-9800}"
    healthcheck:
      test: ["CMD", "python", "-c", "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('WEB_PORT', '9800') + '/healthz', timeout=3).close()"]
      interval: 30s
      timeout: 5s
      start_period: 45s
      retries: 3
EOF
    compose_args+=(-f compose.yaml)
  fi
  for file in compose.override.yaml compose.override.yml docker-compose.override.yml docker-compose.override.yaml; do
    if [[ -f "${file}" ]]; then
      compose_args+=(-f "${file}")
      break
    fi
  done
fi

if [[ -n "${COMPOSE_PROJECT_NAME:-}" ]]; then
  compose_args+=(--project-name "${COMPOSE_PROJECT_NAME}")
fi
if [[ -e "${IMAGE_OVERRIDE}" || -L "${IMAGE_OVERRIDE}" ]]; then
  if [[ -L "${IMAGE_OVERRIDE}" ]] || ! grep -Fxq "${IMAGE_MARKER}" "${IMAGE_OVERRIDE}"; then
    echo "[miyin] ${IMAGE_OVERRIDE} is not managed by this installer. Keep a backup and choose a different filename for that override." >&2
    exit 1
  fi
fi

init_script="${SCRIPT_DIR}/../init_env.sh"
if [[ ! -f "${init_script}" ]]; then
  init_script="$work/init_env.sh"
  download "${RAW_REPO}/scripts/linux/init_env.sh" "${init_script}"
fi
if [[ ! -e .env && ! -L .env && ! -f .env.example ]]; then
  template="${SCRIPT_DIR}/../../../.env.example"
  if [[ ! -f "${template}" ]]; then
    template="$work/env.example"
    download "${RAW_REPO}/.env.example" "${template}"
  fi
  run_privileged cp -- "${template}" .env.example
fi
run_privileged bash "${init_script}" "${APP_DIR}" --repair-auth

services="$(run_privileged docker compose "${compose_args[@]}" config --services)"
if ! grep -Fxq app <<< "${services}"; then
  echo "[miyin] the selected Compose project does not define an app service" >&2
  exit 1
fi

echo "[miyin] pulling ${IMAGE}"
run_privileged docker pull "${IMAGE}"
override_tmp="$(run_privileged mktemp "./.compose.miyin-image.XXXXXX")"
{
  printf '%s\n' "${IMAGE_MARKER}"
  printf 'services:\n  app:\n    image: %s\n    pull_policy: never\n' "${IMAGE}"
} | run_privileged tee "${override_tmp}" >/dev/null
run_privileged chmod 644 "${override_tmp}"
run_privileged mv -f -- "${override_tmp}" "${IMAGE_OVERRIDE}"
override_tmp=""

up_args=(up -d --no-build)
if [[ "$(run_privileged docker compose up --help)" == *"--wait-timeout"* ]]; then
  up_args+=(--wait --wait-timeout 150)
fi
run_privileged docker compose "${compose_args[@]}" -f "${IMAGE_OVERRIDE}" "${up_args[@]}" app
echo "[miyin] Docker deployment updated to ${IMAGE}"
run_privileged docker compose "${compose_args[@]}" -f "${IMAGE_OVERRIDE}" ps app
