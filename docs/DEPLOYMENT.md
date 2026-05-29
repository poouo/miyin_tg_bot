# Deployment

## Docker (Single Container + SQLite)

1. Edit `.env`
2. Run `docker compose up -d --build`
3. Open `http://<ip>:9800`
4. Default admin password is `admin` (change it in dashboard after first login)

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
