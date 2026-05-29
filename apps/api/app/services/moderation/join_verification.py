from datetime import datetime, timedelta, timezone
from random import randint

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.models.entities import VerificationChallenge
from apps.api.app.services.runtime_config_service import get_runtime_config


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_math_question() -> tuple[str, str]:
    a = randint(1, 9)
    b = randint(1, 9)
    return f"{a} + {b} = ?", str(a + b)


async def create_challenge(db: AsyncSession, chat_id: int, user_id: int) -> VerificationChallenge:
    question, answer = create_math_question()
    runtime = await get_runtime_config(db)
    expires_at = _now() + timedelta(seconds=runtime.join_verify_timeout_sec)

    result = await db.execute(
        select(VerificationChallenge).where(
            and_(VerificationChallenge.chat_id == chat_id, VerificationChallenge.user_id == user_id)
        )
    )
    entity = result.scalar_one_or_none()
    if entity is None:
        entity = VerificationChallenge(
            chat_id=chat_id,
            user_id=user_id,
            question=question,
            answer=answer,
            expires_at=expires_at,
            passed=False,
        )
        db.add(entity)
    else:
        entity.question = question
        entity.answer = answer
        entity.expires_at = expires_at
        entity.passed = False

    await db.commit()
    await db.refresh(entity)
    return entity


async def get_challenge(db: AsyncSession, chat_id: int, user_id: int) -> VerificationChallenge | None:
    result = await db.execute(
        select(VerificationChallenge).where(
            and_(VerificationChallenge.chat_id == chat_id, VerificationChallenge.user_id == user_id)
        )
    )
    return result.scalar_one_or_none()


async def verify_challenge(db: AsyncSession, chat_id: int, user_id: int, user_answer: str) -> bool:
    challenge = await get_challenge(db, chat_id, user_id)
    if challenge is None or challenge.passed:
        return False
    if challenge.expires_at < _now():
        return False
    if challenge.answer.strip() != user_answer.strip():
        return False

    challenge.passed = True
    await db.commit()
    return True


async def list_expired_unpassed(db: AsyncSession) -> list[VerificationChallenge]:
    result = await db.execute(
        select(VerificationChallenge).where(
            and_(VerificationChallenge.passed.is_(False), VerificationChallenge.expires_at < _now())
        )
    )
    return list(result.scalars().all())
