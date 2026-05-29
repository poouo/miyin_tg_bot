#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/poouo/miyin_tg_bot.git"
APP_DIR="${APP_DIR:-/opt/miyin_tg_bot}"
BRANCH="${BRANCH:-main}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-${APP_DIR}/.venv}"
RUN_LOG="${APP_DIR}/logs/app.log"
PID_FILE="${APP_DIR}/run/app.pid"
CHECKER_PID_FILE="${APP_DIR}/run/update_checker.pid"
UPDATE_STATUS_FILE="${APP_DIR}/data/update_status.json"

ensure_repo() {
  if [[ ! -d "${APP_DIR}/.git" ]]; then
    mkdir -p "${APP_DIR}"
    git clone -b "${BRANCH}" "${REPO_URL}" "${APP_DIR}"
  else
    cd "${APP_DIR}"
    git fetch origin "${BRANCH}"
    git checkout -B "${BRANCH}" "origin/${BRANCH}"
    git reset --hard "origin/${BRANCH}"
  fi
}

ensure_runtime_dirs() {
  mkdir -p "${APP_DIR}/logs" "${APP_DIR}/run" "${APP_DIR}/data"
}

start_app_nohup() {
  ensure_runtime_dirs
  cd "${APP_DIR}"
  if [[ -f "${PID_FILE}" ]] && kill -0 "$(cat "${PID_FILE}")" >/dev/null 2>&1; then
    echo "app 已在运行 pid=$(cat "${PID_FILE}")"
    return
  fi
  nohup "${VENV_DIR}/bin/python" -m apps.runner.main >>"${RUN_LOG}" 2>&1 &
  echo $! > "${PID_FILE}"
  echo "app started pid=$(cat "${PID_FILE}")"
}

stop_app_nohup() {
  if [[ -f "${PID_FILE}" ]]; then
    pid="$(cat "${PID_FILE}")"
    if kill -0 "${pid}" >/dev/null 2>&1; then
      kill "${pid}" || true
      sleep 1
    fi
    rm -f "${PID_FILE}"
  fi
}

start_update_checker() {
  ensure_runtime_dirs
  cd "${APP_DIR}"
  if [[ -f "${CHECKER_PID_FILE}" ]] && kill -0 "$(cat "${CHECKER_PID_FILE}")" >/dev/null 2>&1; then
    echo "update checker 已运行 pid=$(cat "${CHECKER_PID_FILE}")"
    return
  fi
  nohup bash "${APP_DIR}/scripts/linux/local/update_checker.sh" >>"${APP_DIR}/logs/update_checker.log" 2>&1 &
  echo $! > "${CHECKER_PID_FILE}"
  echo "update checker started pid=$(cat "${CHECKER_PID_FILE}")"
}

stop_update_checker() {
  if [[ -f "${CHECKER_PID_FILE}" ]]; then
    pid="$(cat "${CHECKER_PID_FILE}")"
    if kill -0 "${pid}" >/dev/null 2>&1; then
      kill "${pid}" || true
      sleep 1
    fi
    rm -f "${CHECKER_PID_FILE}"
  fi
}
