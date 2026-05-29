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
    source <(curl -fsSL "${COMMON_URL}")
  elif command -v wget >/dev/null 2>&1; then
    source <(wget -qO- "${COMMON_URL}")
  else
    echo "curl or wget is required to load _common.sh"
    exit 1
  fi
fi

echo "[miyin] local install start"

run_privileged() {
  if [[ "${EUID}" -eq 0 ]]; then
    "$@"
  else
    sudo "$@"
  fi
}

python_version() {
  local pybin="$1"
  "${pybin}" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
}

python_supported() {
  local pybin="$1"
  local ver
  ver="$(python_version "${pybin}")"
  local major="${ver%%.*}"
  local minor="${ver##*.}"
  if [[ "${major}" -ne 3 ]]; then
    return 1
  fi
  # Current pinned dependencies are stable on <= 3.12.
  if (( minor > 12 )); then
    return 1
  fi
  if (( minor < 10 )); then
    return 1
  fi
  return 0
}

ensure_supported_python() {
  local preferred="${PYTHON_BIN:-python3}"
  local candidates=("${preferred}" python3.12 python3.11 python3.10 python3)
  local py

  for py in "${candidates[@]}"; do
    if command -v "${py}" >/dev/null 2>&1 && python_supported "${py}"; then
      PYTHON_BIN="${py}"
      export PYTHON_BIN
      echo "[miyin] using Python: ${PYTHON_BIN} ($(python_version "${PYTHON_BIN}"))"
      return 0
    fi
  done

  if command -v apt-get >/dev/null 2>&1; then
    echo "[miyin] no supported Python found, installing python3.12 + venv..."
    run_privileged apt-get update
    run_privileged apt-get install -y python3.12 python3.12-venv || true

    if command -v python3.12 >/dev/null 2>&1 && python_supported python3.12; then
      PYTHON_BIN="python3.12"
      export PYTHON_BIN
      echo "[miyin] using Python: ${PYTHON_BIN} ($(python_version "${PYTHON_BIN}"))"
      return 0
    fi
  fi

  echo "[miyin] failed to find/install a supported Python (3.10~3.12)."
  echo "[miyin] please install python3.12 and retry:"
  echo "  apt-get update && apt-get install -y python3.12 python3.12-venv"
  exit 1
}

ensure_venv_support() {
  if "${PYTHON_BIN}" -m ensurepip --version >/dev/null 2>&1; then
    return 0
  fi

  echo "[miyin] ensurepip not available, installing venv package..."

  if command -v apt-get >/dev/null 2>&1; then
    local py_minor
    py_minor="$("${PYTHON_BIN}" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")"
    local pkg_minor="python${py_minor}-venv"

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

ensure_build_toolchain() {
  if ! command -v apt-get >/dev/null 2>&1; then
    return 0
  fi

  local py_minor
  py_minor="$("${PYTHON_BIN}" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")"
  local py_dev_pkg="python${py_minor}-dev"

  echo "[miyin] ensuring build dependencies for native wheels..."
  run_privileged apt-get update
  run_privileged apt-get install -y \
    build-essential \
    "${py_dev_pkg}" \
    pkg-config \
    libffi-dev \
    libssl-dev \
    rustc \
    cargo || true

  # Fallback for distros without versioned python-dev package.
  if ! dpkg -s "${py_dev_pkg}" >/dev/null 2>&1; then
    run_privileged apt-get install -y python3-dev || true
  fi
}

ensure_repo
ensure_runtime_dirs
cd "${APP_DIR}"

ensure_supported_python
ensure_venv_support
ensure_build_toolchain

need_recreate_venv=false
if [[ ! -d "${VENV_DIR}" ]] || [[ ! -x "${VENV_DIR}/bin/python" ]] || [[ ! -x "${VENV_DIR}/bin/pip" ]]; then
  need_recreate_venv=true
else
  venv_ver="$("${VENV_DIR}/bin/python" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || true)"
  target_ver="$(python_version "${PYTHON_BIN}")"
  if [[ "${venv_ver}" != "${target_ver}" ]]; then
    need_recreate_venv=true
  fi
fi

if [[ "${need_recreate_venv}" == "true" ]]; then
  echo "[miyin] creating or repairing virtual environment..."
  "${PYTHON_BIN}" -m venv --clear "${VENV_DIR}"
fi

"${VENV_DIR}/bin/python" -m pip install --upgrade pip
"${VENV_DIR}/bin/python" -m pip install --prefer-binary -r "${APP_DIR}/requirements.txt"

if [[ ! -f "${APP_DIR}/.env" ]]; then
  cp "${APP_DIR}/.env.example" "${APP_DIR}/.env"
  echo "[miyin] created .env, please set BOT token and DeepSeek API key"
fi

start_app_nohup
start_update_checker

echo "[miyin] local install done"
echo "[miyin] web: http://<server-ip>:9800"
echo "[miyin] update status file: ${UPDATE_STATUS_FILE}"
