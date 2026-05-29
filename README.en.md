# Miyin TG Group Manager Bot

Current version: `V1.0.00`

Default Web language: Chinese (switchable to English in admin panel).

中文说明: [README.md](./README.md)

## Features

- Join verification (challenge + timeout handling)
- Keyword filtering (delete or mute)
- Ad detection and block
- Anti-spam rate limit
- Auto recovery (unmute after timeout)
- DeepSeek API replies in groups
- Web admin panel (Chinese/English switch)
- Password login for admin panel, token valid for 10 days
- Temporary login ban after repeated failures (configurable)
- Manual moderation commands restricted to group owner/admin
- Docker single-container deployment (SQLite)
- Local one-click deploy/upgrade/uninstall
- Version-based update check and online update

## Quick Start

1. Copy env file

```bash
cp .env.example .env
```

2. Configure at least:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_BOT_USERNAME`
- `DEEPSEEK_API_KEY`
- `WEB_ADMIN_PASSWORD`
- `WEB_AUTH_SECRET`

3. Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m apps.runner.main
```

Default web URL: `http://127.0.0.1:9800`

## Docker (Single Container + SQLite)

```bash
docker compose up -d --build
```

## One-click Scripts (GitHub)

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

## Version Update Policy

- Root `VERSION` file is the version source (`V1.0.00`)
- Update check compares local `VERSION` with remote `VERSION`
- `has_update=true` when remote version is newer

