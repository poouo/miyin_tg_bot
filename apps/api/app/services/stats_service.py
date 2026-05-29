from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.models.entities import GroupConfig, KeywordRule, ModerationLog


async def dashboard_stats(db: AsyncSession) -> dict:
    group_count = (await db.execute(select(func.count()).select_from(GroupConfig))).scalar_one()
    keyword_count = (await db.execute(select(func.count()).select_from(KeywordRule))).scalar_one()
    log_count = (await db.execute(select(func.count()).select_from(ModerationLog))).scalar_one()
    return {
        "group_count": group_count,
        "keyword_count": keyword_count,
        "log_count": log_count,
    }

