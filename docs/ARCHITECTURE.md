# Architecture

## Runtime model

- 单进程运行：`apps.runner.main`
- 进程内并发：
  - FastAPI Web/API 服务
  - Aiogram Bot 轮询任务
  - 风控后台任务（自动恢复、验证超时处理）

## Core modules

- `group_service`: 群配置管理
- `keyword_service`: 关键词规则
- `deepseek_client`: OpenAI 兼容 AI 对接（DeepSeek / OpenCode / 自定义，服务商在后台切换）
- `ai_ad_guard`: AI 广告分档处理、群 AI 回复发送前审核、代发广告的 30 天警告计数
- `moderation/policy.py`: 统一风控决策
- `moderation/join_verification.py`: 入群验证
- `moderation/anti_spam.py`: 防刷屏
- `moderation/ad_block.py`: 广告识别
- `moderation/auto_recover.py`: 自动恢复
- `update_service.py`: 检查更新/在线更新触发

## Data layer

- SQLAlchemy + SQLite (`data/miyin.db`)
- 关键表：
  - `group_configs`
  - `keyword_rules`
  - `moderation_logs`
  - `verification_challenges`
  - `user_sanctions`

