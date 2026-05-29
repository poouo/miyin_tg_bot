# Miyin TG Group Manager Bot

一个运行在 Linux 的 Telegram 群组管理机器人，包含 Web 管理后台、DeepSeek 智能问答和完整风控能力。

## 功能清单

- 入群用户验证（数学题挑战 + 超时自动移出）
- 关键词过滤（删除/禁言策略）
- 广告识别与封禁撤回
- 防刷屏（时间窗限频）
- 关键词/广告/刷屏触发后的自动恢复（定时解禁）
- DeepSeek API 回答群友问题（`/ask`、@机器人、`问:`）
- Web 管理界面（群配置、关键词规则、更新管理）
- Docker 单容器部署（SQLite）
- 本地一键部署/升级/卸载（支持后台检查更新 + 在线更新）

## 架构

- `apps/api`: FastAPI 管理端 + 管理后台页面 + REST API
- `apps/bot`: aiogram Telegram 机器人
- `apps/runner`: 单进程运行 API + Bot
- `apps/api/app/services/moderation`: 风控策略引擎
- `scripts/linux/docker`: Docker 一键脚本
- `scripts/linux/local`: 本地一键脚本（含更新检查与在线更新）
- `infra/docker`: 单容器构建文件
- `data/miyin.db`: SQLite 数据库文件

## 快速开始

1) 配置环境变量

```bash
cp .env.example .env
```

必须至少填写：

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_BOT_USERNAME`
- `DEEPSEEK_API_KEY`

2) 本地运行

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m apps.runner.main
```

管理台默认地址：`http://127.0.0.1:8080`

## Docker 单容器部署

```bash
docker compose up -d --build
```

## 一键脚本（从 GitHub 拉取）

仓库地址：`https://github.com/poouo/miyin_tg_bot.git`

Docker:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/docker/install.sh)
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/docker/upgrade.sh)
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/docker/uninstall.sh)
```

本地:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/local/install.sh)
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/local/upgrade.sh)
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/local/uninstall.sh)
```

## 本地更新能力

- 后台检查更新进程：`scripts/linux/local/update_checker.sh`
- 状态文件：`data/update_status.json`
- 在线更新脚本：`scripts/linux/local/online_update.sh`
- Web 更新接口：
  - `GET /api/v1/updates/background-status`
  - `GET /api/v1/updates/check`
  - `POST /api/v1/updates/online`

## 管理 API 示例

- `POST /api/v1/groups`: 创建/更新群配置
- `PATCH /api/v1/groups/{chat_id}`: 开关功能
- `GET /api/v1/groups/{chat_id}/keywords`: 查看关键词规则
- `POST /api/v1/groups/{chat_id}/keywords`: 新增关键词规则
- `GET /api/v1/groups/{chat_id}/logs`: 查询风控日志
- `POST /api/v1/ai/ask`: 直接调用 DeepSeek 问答

