#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMON_PATH="${SCRIPT_DIR}/_common.sh"
if [[ -f "${COMMON_PATH}" ]]; then
  source "${COMMON_PATH}"
else
  BRANCH="${BRANCH:-main}"
  COMMON_URL="https://raw.githubusercontent.com/poouo/miyin_tg_bot/${BRANCH}/scripts/linux/local/_common.sh"
  if command -v curl >/dev/null 2>&1; then
    # Support direct execution via: bash <(curl ...)
    source <(curl -fsSL "${COMMON_URL}")
  elif command -v wget >/dev/null 2>&1; then
    source <(wget -qO- "${COMMON_URL}")
  else
    echo "curl or wget is required to load _common.sh"
    exit 1
  fi
fi

echo "[miyin] local install start"

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "python not found: ${PYTHON_BIN}"
  echo "please install python3 first"
  exit 1
fi

run_privileged() {
  if [[ "${EUID}" -eq 0 ]]; then
    "$@"
  else
    sudo "$@"
  fi
}

ensure_venv_support() {
  if "${PYTHON_BIN}" -m ensurepip --version >/dev/null 2>&1; then
    return 0
  fi

  echo "[miyin] ensurepip not available, installing python venv package..."

  if command -v apt-get >/dev/null 2>&1; then
    py_minor="$("${PYTHON_BIN}" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")"
    pkg_minor="python${py_minor}-venv"

    run_privileged apt-get update
    if ! run_privileged apt-get install -y "${pkg_minor}"; then
      run_privileged apt-get install -y python3-venv
    fi
  else
    echo "[miyin] unsupported package manager, install python3-venv manually"
    exit 1
  fi

  if ! "${PYTHON_BIN}" -m ensurepip --version >/dev/null 2>&1; then
    echo "[miyin] ensurepip still unavailable after package install"
    exit 1
  fi
}

ensure_repo
ensure_runtime_dirs
cd "${APP_DIR}"

ensure_venv_support

if [[ ! -d "${VENV_DIR}" ]] || [[ ! -x "${VENV_DIR}/bin/python" ]] || [[ ! -x "${VENV_DIR}/bin/pip" ]]; then
  echo "[miyin] creating or repairing virtual environment..."
  "${PYTHON_BIN}" -m venv --clear "${VENV_DIR}"
fi

"${VENV_DIR}/bin/python" -m pip install --upgrade pip
"${VENV_DIR}/bin/python" -m pip install -r "${APP_DIR}/requirements.txt"

if [[ ! -f "${APP_DIR}/.env" ]]; then
  cp "${APP_DIR}/.env.example" "${APP_DIR}/.env"
  echo "[miyin] created .env, please set BOT token and DeepSeek API key"
fi

start_app_nohup
start_update_checker

echo "[miyin] local install done"
echo "[miyin] web: http://<server-ip>:9800"
echo "[miyin] update status file: ${UPDATE_STATUS_FILE}"
