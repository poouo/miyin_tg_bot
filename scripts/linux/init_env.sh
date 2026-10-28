#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${1:-/opt/miyin_tg_bot}"
ENV_PATH="${APP_DIR}/.env"

if [[ -e "${ENV_PATH}" || -L "${ENV_PATH}" ]]; then
  echo "[miyin] existing .env preserved; existing deployments must rotate default credentials separately"
  exit 0
fi

if [[ ! -f "${APP_DIR}/.env.example" ]]; then
  echo "[miyin] .env.example missing: ${APP_DIR}" >&2
  exit 1
fi

random_hex() {
  local value
  value="$(od -An -N32 -tx1 /dev/urandom | tr -d '[:space:]')"
  if [[ ! "${value}" =~ ^[0-9a-f]{64}$ ]]; then
    echo "[miyin] failed to generate secure random credentials" >&2
    return 1
  fi
  printf '%s' "${value}"
}

auth_secret="$(random_hex)"
admin_password="$(random_hex)"

umask 077
env_tmp="$(mktemp "${APP_DIR}/.env.tmp.XXXXXX")"
trap 'rm -f -- "${env_tmp}"' EXIT
secret_written=false
password_written=false
while IFS= read -r line || [[ -n "${line}" ]]; do
  case "${line}" in
    WEB_AUTH_SECRET=*)
      printf 'WEB_AUTH_SECRET=%s\n' "${auth_secret}"
      secret_written=true
      ;;
    WEB_ADMIN_PASSWORD=*)
      printf 'WEB_ADMIN_PASSWORD=%s\n' "${admin_password}"
      password_written=true
      ;;
    *) printf '%s\n' "${line}" ;;
  esac
done < "${APP_DIR}/.env.example" > "${env_tmp}"
if [[ "${secret_written}" == false ]]; then
  printf 'WEB_AUTH_SECRET=%s\n' "${auth_secret}" >> "${env_tmp}"
fi
if [[ "${password_written}" == false ]]; then
  printf 'WEB_ADMIN_PASSWORD=%s\n' "${admin_password}" >> "${env_tmp}"
fi

# Publish the complete file without overwriting a concurrently created .env.
ln -- "${env_tmp}" "${ENV_PATH}"
echo "[miyin] created .env with a random signing secret and admin password (permissions: 600)"
printf '[miyin] initial admin password: %s\n' "${admin_password}"
echo "[miyin] save this password, then configure bot/deepseek settings in web admin"
