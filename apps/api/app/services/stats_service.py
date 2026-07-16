from datetime import datetime, timedelta, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.models.entities import (
    AdKeyword,
    AutoReplyRule,
    GroupConfig,
    KeywordRule,
    ModerationLog,
    UserSanction,
)


async def dashboard_stats(db: AsyncSession) -> dict:
    now = datetime.now(timezone.utc)
    last_24h = now - timedelta(hours=24)

    def count_rows(model, *conditions):
        query = select(func.count()).select_from(model)
        if conditions:
            query = query.where(*conditions)
        return query.scalar_subquery()

    active_bans = (
        select(func.count())
        .select_from(UserSanction)
        .where(
            UserSanction.sanction_type == "ban",
            UserSanction.recovered.is_(False),
            or_(UserSanction.expires_at.is_(None), UserSanction.expires_at > now),
        )
        .scalar_subquery()
    )
    stmt = select(
        count_rows(GroupConfig).label("group_count"),
        count_rows(AutoReplyRule).label("auto_reply_count"),
        count_rows(KeywordRule).label("keyword_count"),
        count_rows(AdKeyword).label("ad_keyword_count"),
        active_bans.label("active_ban_count"),
        count_rows(ModerationLog, ModerationLog.created_at >= last_24h).label("last_24h_log_count"),
        count_rows(ModerationLog).label("log_count"),
    )
    row = (await db.execute(stmt)).one()
    return {
        "group_count": int(row.group_count),
        "auto_reply_count": int(row.auto_reply_count),
        "keyword_count": int(row.keyword_count),
        "ad_keyword_count": int(row.ad_keyword_count),
        "active_ban_count": int(row.active_ban_count),
        "last_24h_log_count": int(row.last_24h_log_count),
        "log_count": int(row.log_count),
    }

