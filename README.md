# Miyin TG 群组管理机器人

当前版本：`V1.0.00`

默认 Web 语言：中文（可在后台切换英文）。
默认后台密码：`admin`（登录后可在后台修改）。

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
- 支持在后台修改管理员密码
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

## GitHub 一键脚本（逐个执行）

仓库：`https://github.com/poouo/miyin_tg_bot.git`

### Docker 安装脚本

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/docker/install.sh)
```

### Docker 升级脚本

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/docker/upgrade.sh)
```

### Docker 卸载脚本

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/docker/uninstall.sh)
```

### 本地安装脚本

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/local/install.sh)
```

### 本地升级脚本

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/local/upgrade.sh)
```

### 本地卸载脚本

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/poouo/miyin_tg_bot/main/scripts/linux/local/uninstall.sh)
```

