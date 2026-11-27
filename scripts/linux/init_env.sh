#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${1:-/opt/miyin_tg_bot}"
ENV_PATH="${APP_DIR}/.env"
MODE="${2:-}"

random_hex() {
  local value
  value="$(od -An -N32 -tx1 /dev/urandom | tr -d '[:space:]')"
  if [[ ! "${value}" =~ ^[0-9a-f]{64}$ ]]; then
    echo "[miyin] failed to generate secure random credentials" >&2
    return 1
  fi
  printf '%s' "${value}"
}

literal_env_value() {
  local value="$1"
  value="${value#"${value%%[![:space:]]*}"}"
  case "${value:0:1}" in
    "'") value="${value:1}"; value="${value%%\'*}" ;;
    '"') value="${value:1}"; value="${value%%\"*}" ;;
    *) value="${value%%[[:space:]]#*}" ;;
  esac
  value="${value#"${value%%[![:space:]]*}"}"
  printf '%s' "${value%"${value##*[![:space:]]}"}"
}

credential_line='^[[:space:]]*(export[[:space:]]+)?(WEB_AUTH_SECRET|WEB_ADMIN_PASSWORD)[[:space:]]*[:=](.*)$'
secret_needed=true
password_needed=true
repair=false
source_file="${APP_DIR}/.env.example"

if [[ -e "${ENV_PATH}" || -L "${ENV_PATH}" ]]; then
  if [[ "${MODE}" != "--repair-auth" || -L "${ENV_PATH}" ]]; then
    echo "[miyin] existing .env preserved"
    exit 0
  fi
  repair=true
  source_file="${ENV_PATH}"
  current_secret=""
  current_password=""
  while IFS= read -r line || [[ -n "${line}" ]]; do
    if [[ "${line}" =~ ${credential_line} ]]; then
      case "${BASH_REMATCH[2]}" in
        WEB_AUTH_SECRET) current_secret="$(literal_env_value "${BASH_REMATCH[3]}")" ;;
        WEB_ADMIN_PASSWORD) current_password="$(literal_env_value "${BASH_REMATCH[3]}")" ;;
      esac
    fi
  done < "${source_file}"

  # Leave interpolated values to Compose. The app can create a key in its data volume if needed.
  if [[ "${current_secret}" == *'$'* || "${current_secret}" == *'\'* ]] ||
     [[ "${#current_secret}" -ge 32 && "${current_secret}" != change_me_to_a_long_random_string &&
        "${current_secret}" != replace_with_long_random_string ]]; then
    secret_needed=false
  fi
  if [[ -f "${APP_DIR}/data/admin_password.json" || "${current_password}" == *'$'* || "${current_password}" == *'\'* ||
        "${#current_password}" -ge 8 ]]; then
    password_needed=false
  fi
  if [[ "${secret_needed}" == false && "${password_needed}" == false ]]; then
    echo "[miyin] existing .env credentials preserved"
    exit 0
  fi
elif [[ ! -f "${source_file}" ]]; then
  echo "[miyin] .env.example missing: ${APP_DIR}" >&2
  exit 1
fi

auth_secret=""
admin_password=""
if [[ "${secret_needed}" == true ]]; then auth_secret="$(random_hex)"; fi
if [[ "${password_needed}" == true ]]; then admin_password="$(random_hex)"; fi

umask 077
env_tmp="$(mktemp "${APP_DIR}/.env.tmp.XXXXXX")"
trap 'rm -f -- "${env_tmp}"' EXIT
secret_written=false
password_written=false
while IFS= read -r line || [[ -n "${line}" ]]; do
  if [[ "${line}" =~ ${credential_line} ]]; then
    case "${BASH_REMATCH[2]}" in
      WEB_AUTH_SECRET)
        if [[ "${secret_needed}" == true ]]; then
          if [[ "${secret_written}" == false ]]; then
            printf 'WEB_AUTH_SECRET=%s\n' "${auth_secret}"
            secret_written=true
          fi
          continue
        fi
        ;;
      WEB_ADMIN_PASSWORD)
        if [[ "${password_needed}" == true ]]; then
          if [[ "${password_written}" == false ]]; then
            printf 'WEB_ADMIN_PASSWORD=%s\n' "${admin_password}"
            password_written=true
          fi
          continue
        fi
        ;;
    esac
  fi
  printf '%s\n' "${line}"
done < "${source_file}" > "${env_tmp}"
if [[ "${secret_needed}" == true && "${secret_written}" == false ]]; then
  printf 'WEB_AUTH_SECRET=%s\n' "${auth_secret}" >> "${env_tmp}"
fi
if [[ "${password_needed}" == true && "${password_written}" == false ]]; then
  printf 'WEB_ADMIN_PASSWORD=%s\n' "${admin_password}" >> "${env_tmp}"
fi

if [[ "${repair}" == true ]]; then
  if [[ "${EUID}" -eq 0 && "${OSTYPE}" == linux* ]]; then
    chown --reference="${ENV_PATH}" "${env_tmp}"
  fi
  mv -f -- "${env_tmp}" "${ENV_PATH}"
  echo "[miyin] repaired outdated admin credentials in .env"
else
  # Publish without overwriting a concurrently created .env.
  ln -- "${env_tmp}" "${ENV_PATH}"
  echo "[miyin] created .env with a random signing secret and admin password (permissions: 600)"
fi
if [[ "${password_needed}" == true ]]; then
  printf '[miyin] initial admin password: %s\n' "${admin_password}"
  echo "[miyin] a password previously saved in the dashboard still takes precedence"
fi
