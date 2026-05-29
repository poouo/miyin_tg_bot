# Miyin TG Group Manager Bot

Telegram group management bot for Linux with Web admin, DeepSeek AI replies, and moderation automation.

## Features

- Join verification challenge
- Keyword filtering (delete or mute)
- Ad message block + sanction
- Anti-spam rate limit
- Auto recover (unmute after timeout)
- DeepSeek API answering in groups
- Web admin dashboard
- Web password login
- Admin token validity: 10 days
- Login brute-force protection (enable/disable + attempts + ban minutes)
- Docker one-container deployment (SQLite)
- Local one-click deploy/upgrade/uninstall
- Background update check + online update trigger

## Quick Start

1. Copy env:

```bash
cp .env.example .env
```

2. Edit required values:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_BOT_USERNAME`
- `DEEPSEEK_API_KEY`
- `WEB_ADMIN_PASSWORD`
- `WEB_AUTH_SECRET`

3. Run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m apps.runner.main
```

Web dashboard: `http://127.0.0.1:8080`

## Docker (single container + SQLite)

```bash
docker compose up -d --build
```

## One-click scripts (from GitHub)

Repo: `https://github.com/poouo/miyin_tg_bot.git`

Docker:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/docker/install.sh)
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/docker/upgrade.sh)
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/docker/uninstall.sh)
```

Local:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/local/install.sh)
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/local/upgrade.sh)
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/local/uninstall.sh)
```

## Admin Security APIs

- `GET /api/v1/security/login`
- `PUT /api/v1/security/login`

## Update APIs

- `GET /api/v1/updates/background-status`
- `GET /api/v1/updates/check`
- `POST /api/v1/updates/online`

