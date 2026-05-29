from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.models.entities import LoginAttempt, SecurityConfig
from apps.api.app.schemas.security import SecurityConfigUpdate


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


async def get_or_create_security_config(db: AsyncSession) -> SecurityConfig:
    result = await db.execute(select(SecurityConfig).limit(1))
    entity = result.scalar_one_or_none()
    if entity is not None:
        return entity

    entity = SecurityConfig()
    db.add(entity)
    await db.commit()
    await db.refresh(entity)
    return entity


async def update_security_config(db: AsyncSession, payload: SecurityConfigUpdate) -> SecurityConfig:
    entity = await get_or_create_security_config(db)
    entity.login_ban_enabled = payload.login_ban_enabled
    entity.login_max_attempts = payload.login_max_attempts
    entity.login_ban_minutes = payload.login_ban_minutes
    await db.commit()
    await db.refresh(entity)
    return entity


async def get_or_create_login_attempt(db: AsyncSession, ip: str) -> LoginAttempt:
    result = await db.execute(select(LoginAttempt).where(LoginAttempt.ip == ip))
    entity = result.scalar_one_or_none()
    if entity is not None:
        return entity

    entity = LoginAttempt(ip=ip, fail_count=0, banned_until=None)
    db.add(entity)
    await db.commit()
    await db.refresh(entity)
    return entity


async def check_login_allowed(db: AsyncSession, ip: str) -> tuple[bool, int]:
    config = await get_or_create_security_config(db)
    if not config.login_ban_enabled:
        return True, 0

    record = await get_or_create_login_attempt(db, ip)
    banned_until = normalize_utc(record.banned_until)
    if banned_until and banned_until > utc_now():
        minutes = int((banned_until - utc_now()).total_seconds() // 60) + 1
        return False, max(1, minutes)
    return True, 0


async def register_failed_login(db: AsyncSession, ip: str) -> None:
    config = await get_or_create_security_config(db)
    record = await get_or_create_login_attempt(db, ip)
    record.fail_count += 1

    if config.login_ban_enabled and record.fail_count >= config.login_max_attempts:
        record.banned_until = utc_now() + timedelta(minutes=config.login_ban_minutes)
        record.fail_count = 0

    await db.commit()


async def clear_login_attempt(db: AsyncSession, ip: str) -> None:
    record = await get_or_create_login_attempt(db, ip)
    record.fail_count = 0
    record.banned_until = None
    await db.commit()

