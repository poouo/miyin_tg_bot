# Deployment

## Docker (Single Container + SQLite)

1. Edit `.env`
2. Run `docker compose up -d --build`
3. Open `http://<ip>:9800`

## Linux Local Deploy

1. Run `scripts/linux/local/install.sh`
2. The installer will:
   - pull source code from GitHub
   - create venv and install dependencies
   - start `apps.runner.main`
   - start background update checker

## Local Update Workflow

- Passive check:
  - `update_checker.sh` runs `git fetch` periodically
  - writes status into `data/update_status.json`
- Online update:
  - web calls `/api/v1/updates/online`
  - backend triggers `online_update.sh`
  - auto pulls code, installs deps, restarts service

