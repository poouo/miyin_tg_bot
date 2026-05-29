# Deployment

## Docker (single container)

1. 编辑 `.env`
2. 执行 `docker compose up -d --build`
3. 打开 `http://<ip>:8080`

## Linux local deploy

1. 执行 `scripts/linux/local/install.sh`
2. 安装脚本会：
   - 拉取 GitHub 仓库
   - 创建 venv + 安装依赖
   - 启动 `apps.runner.main`
   - 启动后台更新检查进程

## Local update workflow

- 被动检查更新：
  - `update_checker.sh` 周期执行 `git fetch`
  - 将结果写入 `data/update_status.json`
- 在线更新：
  - Web 调用 `/api/v1/updates/online`
  - 后台执行 `online_update.sh`
  - 自动拉取代码、安装依赖、重启服务

