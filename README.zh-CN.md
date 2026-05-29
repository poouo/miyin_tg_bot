# Miyin TG 群组管理机器人

当前版本：`V1.0.00`

默认 Web 语言：中文（可在后台切换为英文）。

English readme: [README.en.md](./README.en.md)

## 功能特性

- 入群验证（挑战题 + 超时处理）
- 关键词过滤（删除或禁言）
- 广告识别与拦截
- 防刷屏限频
- 自动恢复（到期自动解除禁言）
- DeepSeek API 群内问答
- Web 管理后台（支持中英文切换）
- 管理后台密码登录，token 有效期 10 天
- 登录失败多次临时封禁（可配置开关、次数、分钟数）
- 手动管理指令仅群主/管理员可用
- Docker 单容器部署（SQLite）
- 本地一键部署/升级/卸载
- 基于版本号的更新检测与在线升级

## 快速开始

1. 复制环境变量文件

```bash
cp .env.example .env
```

2. 至少配置以下项

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_BOT_USERNAME`
- `DEEPSEEK_API_KEY`
- `WEB_ADMIN_PASSWORD`
- `WEB_AUTH_SECRET`

3. 本地运行

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m apps.runner.main
```

Web 后台默认地址：`http://127.0.0.1:9800`

## Docker（单容器 + SQLite）

```bash
docker compose up -d --build
```

## GitHub 一键脚本

仓库：`https://github.com/poouo/miyin_tg_bot.git`

Docker：

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/docker/install.sh)
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/docker/upgrade.sh)
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/docker/uninstall.sh)
```

本地：

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/local/install.sh)
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/local/upgrade.sh)
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/local/uninstall.sh)
```

## 版本更新策略

- 项目根目录 `VERSION` 文件为版本号源（当前 `V1.0.00`）
- 更新检测比较本地 `VERSION` 与远端 `VERSION`
- 远端版本更高时返回 `has_update=true`

