from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.models.entities import UserSanction


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def add_mute_sanction(
    db: AsyncSession,
    chat_id: int,
    user_id: int,
    reason: str,
    mute_minutes: int,
) -> UserSanction:
    expires_at = _now() + timedelta(minutes=mute_minutes)
    entity = UserSanction(
        chat_id=chat_id,
        user_id=user_id,
        sanction_type="mute",
        reason=reason,
        expires_at=expires_at,
        recovered=False,
    )
    db.add(entity)
    await db.commit()
    await db.refresh(entity)
    return entity


async def list_recoverable_sanctions(db: AsyncSession) -> list[UserSanction]:
    result = await db.execute(
        select(UserSanction).where(
            and_(
                UserSanction.sanction_type == "mute",
                UserSanction.recovered.is_(False),
                UserSanction.expires_at.is_not(None),
                UserSanction.expires_at < _now(),
            )
        )
    )
    return list(result.scalars().all())


async def mark_recovered(db: AsyncSession, sanction_id: int) -> None:
    result = await db.execute(select(UserSanction).where(UserSanction.id == sanction_id))
    entity = result.scalar_one_or_none()
    if entity is None:
        return
    entity.recovered = True
    await db.commit()

