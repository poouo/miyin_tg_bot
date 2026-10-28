# Deployment

## Docker (Single Container + SQLite)

1. Run `bash scripts/linux/init_env.sh .` to generate `.env` with random credentials, then edit web/db/base settings if needed
2. Run `docker compose up -d --build`
3. Open `http://<ip>:9800`
4. Log in with the initial admin password printed when `.env` was generated
5. Configure TG Bot and DeepSeek runtime parameters in dashboard

Both one-click installers use the same credential generator. It creates a 64-character random signing secret and an independent random admin password, saves `.env` with permissions `600`, and never prints the signing secret. Existing `.env` files are preserved. Existing deployments must rotate default credentials separately; upgrading code alone does not replace them.

## Docker Image Builds

GitHub Actions runs tests and publishes `linux/amd64` and `linux/arm64` images to `ghcr.io/poouo/miyin_tg_bot` on pushes to `main`, version tag pushes, and manual workflow runs. Main builds publish `latest`, the version from `VERSION` (for example `1.0.04`), and a `sha-` tag. Version tag builds publish the version and `sha-` tags. The supplied Compose file continues to build from source.

The Docker build context excludes `.env`, runtime data, databases, and Git metadata. Configure runtime credentials through `.env` and keep persistent data mounted at `/app/data`.

## Linux Local Deploy

1. Run `scripts/linux/local/install.sh`
2. The installer will:
   - pull source code from GitHub
   - create venv and install dependencies
   - start `apps.runner.main`
   - start background update checker

## Script Reference (One by One)

### scripts/linux/docker/install.sh

- Purpose: first-time Docker deployment.
- Command:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/docker/install.sh)
```

### scripts/linux/docker/upgrade.sh

- Purpose: pull latest code and rebuild containers.
- Command:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/docker/upgrade.sh)
```

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
  - `update_checker.sh` runs `git fetch` periodically
  - writes status into `data/update_status.json`
- Online update:
  - web calls `/api/v1/updates/online`
  - backend triggers `online_update.sh`
  - auto pulls code, installs deps, restarts service
