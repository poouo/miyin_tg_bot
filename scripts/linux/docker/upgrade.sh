#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "${SCRIPT_DIR}/install.sh" ]]; then
  exec bash "${SCRIPT_DIR}/install.sh" --upgrade
fi

url="https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/docker/install.sh"
installer="$(mktemp)"
trap 'rm -f -- "$installer"' EXIT
if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$url" -o "$installer"
else
  wget -qO "$installer" "$url"
fi
bash "$installer" --upgrade
