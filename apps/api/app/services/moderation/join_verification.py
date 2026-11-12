import asyncio
from datetime import datetime, timedelta, timezone
from random import randint, shuffle

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.models.entities import VerificationChallenge
from apps.api.app.services.moderation.captcha_image import (
    build_letter_options,
    generate_captcha_text,
    render_captcha_gif,
)
from apps.api.app.services.runtime_config_service import get_runtime_config

# Stored in the `question` column for image challenges. The answer itself only
# lives in the `answer` column, never in logs or messages.
CAPTCHA_QUESTION = "图片验证码（4 个字母）"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _normalize_answer(value: str) -> str:
    # letters are case-insensitive; digits (legacy math challenges) are unaffected
    return value.strip().upper()


def is_challenge_expired(challenge: VerificationChallenge) -> bool:
    return _as_utc(challenge.expires_at) < _now()


def is_challenge_answer_correct(challenge: VerificationChallenge | None, user_answer: str) -> bool:
    if challenge is None or challenge.passed:
        return False
    if is_challenge_expired(challenge):
        return False
    return _normalize_answer(challenge.answer) == _normalize_answer(user_answer)


def create_math_question() -> tuple[str, str]:
    a = randint(1, 9)
    b = randint(1, 9)
    return f"{a} + {b} = ?", str(a + b)


def build_answer_options(answer: str, count: int = 4) -> list[str]:
    try:
        correct = int(answer)
    except Exception:
        return [answer]

    options = {correct}
    while len(options) < max(2, count):
        delta = randint(-5, 5)
        if delta == 0:
            continue
        candidate = correct + delta
        if candidate <= 0:
            continue
        options.add(candidate)

    result = [str(v) for v in options]
    shuffle(result)
    return result


def challenge_failure_reason(challenge: VerificationChallenge | None, user_answer: str) -> str:
    if challenge is None:
        return "验证记录不存在"
    if challenge.passed:
        return "验证已处理"
    if is_challenge_expired(challenge):
        return "验证超时"
    if _normalize_answer(challenge.answer) != _normalize_answer(user_answer):
        return "答案错误"
    return "未通过验证"


async def create_captcha_challenge(
    db: AsyncSession, chat_id: int, user_id: int, message_id: int = 0
) -> tuple[VerificationChallenge, bytes, list[str]]:
    """Create an animated-GIF letter challenge.

    Returns (challenge entity, GIF bytes, four shuffled answer options).
    Rendering is CPU bound, so it runs in a worker thread.
    """
    answer = generate_captcha_text()
    gif_bytes = await asyncio.to_thread(render_captcha_gif, answer)
    options = build_letter_options(answer)
    challenge = await create_challenge(
        db, chat_id, user_id, message_id, question=CAPTCHA_QUESTION, answer=answer
    )
    return challenge, gif_bytes, options


async def create_challenge(
    db: AsyncSession,
    chat_id: int,
    user_id: int,
    message_id: int = 0,
    question: str | None = None,
    answer: str | None = None,
) -> VerificationChallenge:
    if question is None or answer is None:
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
            message_id=message_id,
            expires_at=expires_at,
            passed=False,
        )
        db.add(entity)
    else:
        entity.question = question
        entity.answer = answer
        entity.message_id = message_id
        entity.expires_at = expires_at
        entity.passed = False

    await db.commit()
    await db.refresh(entity)
    return entity


async def set_challenge_message_id(
    db: AsyncSession, chat_id: int, user_id: int, message_id: int
) -> VerificationChallenge | None:
    challenge = await get_challenge(db, chat_id, user_id)
    if challenge is None:
        return None
    challenge.message_id = message_id
    await db.commit()
    await db.refresh(challenge)
    return challenge


async def get_challenge(db: AsyncSession, chat_id: int, user_id: int) -> VerificationChallenge | None:
    result = await db.execute(
        select(VerificationChallenge).where(
            and_(VerificationChallenge.chat_id == chat_id, VerificationChallenge.user_id == user_id)
        )
    )
    return result.scalar_one_or_none()


async def verify_challenge(db: AsyncSession, chat_id: int, user_id: int, user_answer: str) -> bool:
    challenge = await get_challenge(db, chat_id, user_id)
    if not is_challenge_answer_correct(challenge, user_answer):
        return False

    return await mark_challenge_passed(db, challenge)


async def mark_challenge_passed(db: AsyncSession, challenge: VerificationChallenge | None) -> bool:
    if challenge is None or challenge.passed:
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
