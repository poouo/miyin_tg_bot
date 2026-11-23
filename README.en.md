# Miyin TG Group Manager Bot

Current version: `V1.0.05`

Default Web language: Chinese (switchable to English in admin panel).
Installers generate a random signing secret and admin password, and display the initial password in the terminal. Existing `.env` files are preserved; rotate default credentials separately on existing deployments.

Chinese readme: [README.md](./README.md)

## Features

- Join verification (challenge + timeout handling)
- Keyword filtering (delete or mute)
- Ad detection and block
- AI ad detection (1-60s message batching with confidence tiers: delete / warn / mute / kick / ban)
- Two-account spam bait detection: when a mentioned account posts an ad, the @-mention initiator is punished too
- Anti-spam rate limit
- Auto recovery (unmute after timeout)
- AI replies in groups (DeepSeek official / OpenCode / any OpenAI compatible API)
- AI settings can fetch the endpoint model list and pick a model from a dropdown
- Web admin panel (Chinese/English switch)
- Password login for admin panel, token valid for 10 days
- Admin password can be changed in dashboard
- Temporary login ban after repeated failures (configurable)
- Manual moderation commands restricted to group owner/admin
- Docker single-container deployment (SQLite)
- Local one-click deploy/upgrade/uninstall
- Version-based update check and online update

## Quick Start

1. Generate the env file and random admin credentials (existing `.env` files are preserved)

```bash
bash scripts/linux/init_env.sh .
```

2. Configure web service items in `.env`:

- `WEB_AUTH_SECRET`

3. After startup, configure bot and AI runtime values in web dashboard:

- `Bot Token`
- `Bot Username`
- `AI API Key` (choose DeepSeek / OpenCode / custom in the dashboard)

4. Run locally

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

## GitHub One-click Scripts (Run Separately)

Repo: `https://github.com/poouo/miyin_tg_bot.git`

### Docker install script

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/docker/install.sh)
```

### Docker upgrade script

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/docker/upgrade.sh)
```

### Docker uninstall script

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/docker/uninstall.sh)
```

### Local install script

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/local/install.sh)
```

### Local upgrade script

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/local/upgrade.sh)
```

### Local uninstall script

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/local/uninstall.sh)
```
