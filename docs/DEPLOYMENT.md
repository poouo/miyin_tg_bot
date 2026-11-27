# Deployment

## Docker (Single Container + SQLite)

1. Run the Docker install command below on the host. It pulls the official image from GHCR and uses `/opt/miyin_tg_bot` by default.
2. Open `http://<ip>:9800` and log in with the initial admin password printed by the installer.
3. Configure the Telegram bot and AI provider in the dashboard.

Both installers use the same credential generator. Docker install and upgrade repair outdated literal signing secrets in `.env` and generate a new initial password only if it is weak or missing and there is no saved password in `data/admin_password.json`. Other settings and the database are preserved. An existing dashboard password still takes precedence. If a Docker container still receives an invalid signing secret, it generates a private fallback key at `/app/data/admin_session_secret`. Keep this file in the persistent data volume. Rotating the key invalidates older web sessions.

Set unique credentials for manual deployments. A supplied signing secret must have at least 32 characters and an initial admin password at least 8 characters. If you terminate HTTPS at a reverse proxy, set `WEB_TRUSTED_PROXIES` to the proxy addresses so Uvicorn can resolve the client IP and HTTPS scheme. Keep the proxy list limited to proxies you control.

Environment variables such as `TELEGRAM_BOT_TOKEN` initialize missing runtime settings on first startup. Settings already saved in the database take precedence.

## Docker Image Builds

GitHub Actions runs tests and publishes `linux/amd64` and `linux/arm64` images to `ghcr.io/poouo/miyin_tg_bot` on pushes to `main`, version tag pushes, and manual workflow runs. Main builds publish `latest`, the version from `VERSION`, and a `sha-` tag. The repository's `docker-compose.yml` also supports optional manual source builds.

The Docker build context excludes `.env`, runtime data, databases, and Git metadata. Configure runtime credentials through `.env` and keep persistent data mounted at `/app/data`.

The dashboard checks the published `latest` image in GHCR for image deployments and the GitHub source branch for Compose source builds. The one-click scripts default to `latest`. Set `IMAGE_TAG` when running the script to pin a published version. When building from a Git checkout manually, pass the commit and branch so the dashboard can detect updates even when `VERSION` stays the same.

```bash
MIYIN_BUILD_REVISION="$(git rev-parse HEAD)" MIYIN_BUILD_BRANCH="$(git symbolic-ref --short HEAD)" docker compose up -d --build
```

Images built without commit metadata compare their `VERSION` file with GitHub.

## Linux Local Deploy

1. Run `scripts/linux/local/install.sh`
2. The installer will:
   - pull source code from GitHub
   - create venv and install dependencies
   - start `apps.runner.main`
   - start background update checker

## Script Reference (One by One)

### scripts/linux/docker/install.sh

- Purpose: install from the published GHCR image.
- Command:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/docker/install.sh)
```

### scripts/linux/docker/upgrade.sh

- Purpose: pull the published image and recreate the `app` service without building it. Legacy installs keep their existing Compose files, ports, volumes, and data. The script adds `compose.miyin-image.yaml` as an override.
- Command:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/docker/upgrade.sh)
```

Set `APP_DIR` before the command if your deployment lives outside `/opt/miyin_tg_bot`. For custom deployments, set `COMPOSE_FILE` and `COMPOSE_PROJECT_NAME` to match the original project if you used them. To manage an upgraded deployment manually, include `-f compose.miyin-image.yaml` as the last Compose file, with your original Compose files first.

### scripts/linux/docker/uninstall.sh

- Purpose: stop and uninstall Docker deployment.
- Command:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/docker/uninstall.sh)
```

### scripts/linux/local/install.sh

- Purpose: first-time local deployment.
- Command:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/local/install.sh)
```

### scripts/linux/local/upgrade.sh

- Purpose: run local online upgrade workflow.
- Command:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/local/upgrade.sh)
```

### scripts/linux/local/uninstall.sh

- Purpose: stop and uninstall local deployment.
- Command:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/local/uninstall.sh)
```

## Local Update Workflow

- Passive check:
  - `update_checker.sh` periodically compares the deployed Git branch with its remote branch
  - writes status into `data/update_status.json`
- Online update:
  - web calls `/api/v1/updates/online`
  - backend triggers `online_update.sh`
  - fast-forwards a clean checkout, installs dependencies, and restarts the service

## Moderating Messages From Other Bots

To receive group messages from other bots, enable Bot-to-Bot Communication Mode for the moderation bot in BotFather and make it a group administrator with permission to delete messages. Enable AI ad detection for the group in the dashboard.
