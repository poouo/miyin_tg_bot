from sqlalchemy import and_, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.models.entities import (
    AfkStatus,
    DisabledCommand,
    GlobalBan,
    LockConfig,
    LogChannelConfig,
    NoteRule,
    ReportConfig,
    RulesConfig,
    RssSubscription,
    UserWarning,
    UserProfile,
    WarningSetting,
    WelcomeConfig,
)


LOCK_TYPES = {"links", "forwards", "media", "stickers", "commands"}
WARN_ACTIONS = {"mute", "kick", "ban"}
DISABLEABLE_COMMANDS = {
    "adminlist",
    "ask",
    "get",
    "id",
    "notes",
    "report",
    "rules",
    "warns",
}


async def get_rules(db: AsyncSession, chat_id: int) -> RulesConfig | None:
    result = await db.execute(select(RulesConfig).where(RulesConfig.chat_id == chat_id))
    return result.scalar_one_or_none()


async def set_rules(db: AsyncSession, chat_id: int, text: str) -> RulesConfig:
    entity = await get_rules(db, chat_id)
    if entity is None:
        entity = RulesConfig(chat_id=chat_id, rules_text=text)
        db.add(entity)
    else:
        entity.rules_text = text
    await db.commit()
    await db.refresh(entity)
    return entity


async def clear_rules(db: AsyncSession, chat_id: int) -> None:
    entity = await get_rules(db, chat_id)
    if entity is None:
        return
    await db.delete(entity)
    await db.commit()


def normalize_note_name(name: str) -> str:
    return name.strip().lstrip("#").lower()[:64]


async def save_note(db: AsyncSession, chat_id: int, name: str, text: str, parse_mode: str = "plain") -> NoteRule:
    normalized = normalize_note_name(name)
    result = await db.execute(select(NoteRule).where(and_(NoteRule.chat_id == chat_id, NoteRule.name == normalized)))
    entity = result.scalar_one_or_none()
    if entity is None:
        entity = NoteRule(chat_id=chat_id, name=normalized, text=text, parse_mode=parse_mode)
        db.add(entity)
    else:
        entity.text = text
        entity.parse_mode = parse_mode
    await db.commit()
    await db.refresh(entity)
    return entity


async def get_note(db: AsyncSession, chat_id: int, name: str) -> NoteRule | None:
    normalized = normalize_note_name(name)
    result = await db.execute(select(NoteRule).where(and_(NoteRule.chat_id == chat_id, NoteRule.name == normalized)))
    return result.scalar_one_or_none()


async def list_notes(db: AsyncSession, chat_id: int) -> list[NoteRule]:
    result = await db.execute(select(NoteRule).where(NoteRule.chat_id == chat_id).order_by(NoteRule.name.asc()))
    return list(result.scalars().all())


async def delete_note(db: AsyncSession, chat_id: int, name: str) -> bool:
    normalized = normalize_note_name(name)
    result = await db.execute(delete(NoteRule).where(and_(NoteRule.chat_id == chat_id, NoteRule.name == normalized)))
    await db.commit()
    return bool(result.rowcount)


async def get_warning_setting(db: AsyncSession, chat_id: int) -> WarningSetting:
    result = await db.execute(select(WarningSetting).where(WarningSetting.chat_id == chat_id))
    entity = result.scalar_one_or_none()
    if entity is not None:
        return entity
    entity = WarningSetting(chat_id=chat_id)
    db.add(entity)
    await db.commit()
    await db.refresh(entity)
    return entity


async def add_warning(
    db: AsyncSession, chat_id: int, user_id: int, admin_id: int, reason: str = ""
) -> tuple[UserWarning, int, WarningSetting]:
    setting = await get_warning_setting(db, chat_id)
    entity = UserWarning(chat_id=chat_id, user_id=user_id, admin_id=admin_id, reason=reason, active=True)
    db.add(entity)
    await db.commit()
    await db.refresh(entity)
    return entity, await count_warnings(db, chat_id, user_id), setting


async def count_warnings(db: AsyncSession, chat_id: int, user_id: int) -> int:
    result = await db.execute(
        select(func.count(UserWarning.id)).where(
            and_(UserWarning.chat_id == chat_id, UserWarning.user_id == user_id, UserWarning.active.is_(True))
        )
    )
    return int(result.scalar_one() or 0)


async def list_warnings(db: AsyncSession, chat_id: int, user_id: int) -> list[UserWarning]:
    result = await db.execute(
        select(UserWarning)
        .where(and_(UserWarning.chat_id == chat_id, UserWarning.user_id == user_id, UserWarning.active.is_(True)))
        .order_by(UserWarning.created_at.asc())
    )
    return list(result.scalars().all())


async def reset_warnings(db: AsyncSession, chat_id: int, user_id: int) -> int:
    result = await db.execute(
        update(UserWarning)
        .where(and_(UserWarning.chat_id == chat_id, UserWarning.user_id == user_id, UserWarning.active.is_(True)))
        .values(active=False)
    )
    await db.commit()
    return int(result.rowcount or 0)


async def update_warning_setting(
    db: AsyncSession,
    chat_id: int,
    warn_limit: int | None = None,
    warn_action: str | None = None,
    minutes: int | None = None,
) -> WarningSetting:
    entity = await get_warning_setting(db, chat_id)
    if warn_limit is not None:
        entity.warn_limit = max(1, min(warn_limit, 20))
    if warn_action in WARN_ACTIONS:
        entity.warn_action = warn_action
    if minutes is not None:
        if entity.warn_action == "ban":
            entity.ban_minutes = max(1, min(minutes, 10080))
        else:
            entity.mute_minutes = max(1, min(minutes, 10080))
    await db.commit()
    await db.refresh(entity)
    return entity


async def get_report_config(db: AsyncSession, chat_id: int) -> ReportConfig:
    result = await db.execute(select(ReportConfig).where(ReportConfig.chat_id == chat_id))
    entity = result.scalar_one_or_none()
    if entity is not None:
        return entity
    entity = ReportConfig(chat_id=chat_id, enabled=True)
    db.add(entity)
    await db.commit()
    await db.refresh(entity)
    return entity


async def set_reports_enabled(db: AsyncSession, chat_id: int, enabled: bool) -> ReportConfig:
    entity = await get_report_config(db, chat_id)
    entity.enabled = enabled
    await db.commit()
    await db.refresh(entity)
    return entity


async def get_lock_config(db: AsyncSession, chat_id: int) -> LockConfig:
    result = await db.execute(select(LockConfig).where(LockConfig.chat_id == chat_id))
    entity = result.scalar_one_or_none()
    if entity is not None:
        return entity
    entity = LockConfig(chat_id=chat_id)
    db.add(entity)
    await db.commit()
    await db.refresh(entity)
    return entity


async def set_lock(db: AsyncSession, chat_id: int, lock_type: str, enabled: bool) -> LockConfig:
    entity = await get_lock_config(db, chat_id)
    if lock_type not in LOCK_TYPES:
        return entity
    setattr(entity, lock_type, enabled)
    await db.commit()
    await db.refresh(entity)
    return entity


async def get_welcome_config(db: AsyncSession, chat_id: int) -> WelcomeConfig:
    result = await db.execute(select(WelcomeConfig).where(WelcomeConfig.chat_id == chat_id))
    entity = result.scalar_one_or_none()
    if entity is not None:
        return entity
    entity = WelcomeConfig(chat_id=chat_id)
    db.add(entity)
    await db.commit()
    await db.refresh(entity)
    return entity


async def update_welcome_config(db: AsyncSession, chat_id: int, **values) -> WelcomeConfig:
    entity = await get_welcome_config(db, chat_id)
    for key, value in values.items():
        if hasattr(entity, key) and value is not None:
            setattr(entity, key, value)
    await db.commit()
    await db.refresh(entity)
    return entity


def render_template(text: str, *, chat_title: str, user_id: int, full_name: str, username: str = "") -> str:
    return (text or "").format(
        chat_title=chat_title,
        fullname=full_name,
        full_name=full_name,
        username=username or "",
        mention=f'<a href="tg://user?id={user_id}">{full_name}</a>',
        id=user_id,
    )


async def get_log_channel(db: AsyncSession, chat_id: int) -> LogChannelConfig:
    result = await db.execute(select(LogChannelConfig).where(LogChannelConfig.chat_id == chat_id))
    entity = result.scalar_one_or_none()
    if entity is not None:
        return entity
    entity = LogChannelConfig(chat_id=chat_id)
    db.add(entity)
    await db.commit()
    await db.refresh(entity)
    return entity


async def set_log_channel(db: AsyncSession, chat_id: int, log_chat_id: int, enabled: bool = True) -> LogChannelConfig:
    entity = await get_log_channel(db, chat_id)
    entity.log_chat_id = log_chat_id
    entity.enabled = enabled
    await db.commit()
    await db.refresh(entity)
    return entity


async def unset_log_channel(db: AsyncSession, chat_id: int) -> LogChannelConfig:
    entity = await get_log_channel(db, chat_id)
    entity.enabled = False
    entity.log_chat_id = 0
    await db.commit()
    await db.refresh(entity)
    return entity


async def get_global_ban(db: AsyncSession, user_id: int) -> GlobalBan | None:
    result = await db.execute(select(GlobalBan).where(GlobalBan.user_id == user_id))
    return result.scalar_one_or_none()


async def add_global_ban(db: AsyncSession, user_id: int, admin_id: int, reason: str = "") -> GlobalBan:
    entity = await get_global_ban(db, user_id)
    if entity is None:
        entity = GlobalBan(user_id=user_id, admin_id=admin_id, reason=reason, active=True)
        db.add(entity)
    else:
        entity.admin_id = admin_id
        entity.reason = reason
        entity.active = True
    await db.commit()
    await db.refresh(entity)
    return entity


async def remove_global_ban(db: AsyncSession, user_id: int) -> bool:
    entity = await get_global_ban(db, user_id)
    if entity is None or not entity.active:
        return False
    entity.active = False
    await db.commit()
    return True


async def list_global_bans(db: AsyncSession) -> list[GlobalBan]:
    result = await db.execute(select(GlobalBan).where(GlobalBan.active.is_(True)).order_by(GlobalBan.created_at.desc()))
    return list(result.scalars().all())


async def is_globally_banned(db: AsyncSession, user_id: int) -> GlobalBan | None:
    entity = await get_global_ban(db, user_id)
    if entity is None or not entity.active:
        return None
    return entity


def normalize_command(command: str) -> str:
    return command.strip().lower().lstrip("/").split("@")[0][:64]


async def disable_command(db: AsyncSession, chat_id: int, command: str) -> DisabledCommand | None:
    normalized = normalize_command(command)
    if normalized not in DISABLEABLE_COMMANDS:
        return None
    result = await db.execute(
        select(DisabledCommand).where(and_(DisabledCommand.chat_id == chat_id, DisabledCommand.command == normalized))
    )
    entity = result.scalar_one_or_none()
    if entity is None:
        entity = DisabledCommand(chat_id=chat_id, command=normalized)
        db.add(entity)
        await db.commit()
        await db.refresh(entity)
    return entity


async def enable_command(db: AsyncSession, chat_id: int, command: str) -> bool:
    normalized = normalize_command(command)
    result = await db.execute(
        delete(DisabledCommand).where(and_(DisabledCommand.chat_id == chat_id, DisabledCommand.command == normalized))
    )
    await db.commit()
    return bool(result.rowcount)


async def list_disabled_commands(db: AsyncSession, chat_id: int) -> list[str]:
    result = await db.execute(
        select(DisabledCommand.command).where(DisabledCommand.chat_id == chat_id).order_by(DisabledCommand.command.asc())
    )
    return list(result.scalars().all())


async def is_command_disabled(db: AsyncSession, chat_id: int, command: str) -> bool:
    normalized = normalize_command(command)
    result = await db.execute(
        select(DisabledCommand.id).where(and_(DisabledCommand.chat_id == chat_id, DisabledCommand.command == normalized))
    )
    return result.first() is not None


async def set_afk(db: AsyncSession, user_id: int, reason: str = "") -> AfkStatus:
    result = await db.execute(select(AfkStatus).where(AfkStatus.user_id == user_id))
    entity = result.scalar_one_or_none()
    if entity is None:
        entity = AfkStatus(user_id=user_id, reason=reason, active=True)
        db.add(entity)
    else:
        entity.reason = reason
        entity.active = True
    await db.commit()
    await db.refresh(entity)
    return entity


async def clear_afk(db: AsyncSession, user_id: int) -> AfkStatus | None:
    result = await db.execute(select(AfkStatus).where(AfkStatus.user_id == user_id))
    entity = result.scalar_one_or_none()
    if entity is None or not entity.active:
        return None
    entity.active = False
    await db.commit()
    await db.refresh(entity)
    return entity


async def get_afk(db: AsyncSession, user_id: int) -> AfkStatus | None:
    result = await db.execute(select(AfkStatus).where(and_(AfkStatus.user_id == user_id, AfkStatus.active.is_(True))))
    return result.scalar_one_or_none()


async def add_rss_subscription(db: AsyncSession, chat_id: int, url: str, title: str = "") -> RssSubscription:
    result = await db.execute(
        select(RssSubscription).where(and_(RssSubscription.chat_id == chat_id, RssSubscription.url == url))
    )
    entity = result.scalar_one_or_none()
    if entity is None:
        entity = RssSubscription(chat_id=chat_id, url=url, title=title, enabled=True)
        db.add(entity)
    else:
        entity.title = title or entity.title
        entity.enabled = True
    await db.commit()
    await db.refresh(entity)
    return entity


async def remove_rss_subscription(db: AsyncSession, chat_id: int, url: str) -> bool:
    result = await db.execute(
        delete(RssSubscription).where(and_(RssSubscription.chat_id == chat_id, RssSubscription.url == url))
    )
    await db.commit()
    return bool(result.rowcount)


async def list_rss_subscriptions(db: AsyncSession, chat_id: int) -> list[RssSubscription]:
    result = await db.execute(
        select(RssSubscription)
        .where(and_(RssSubscription.chat_id == chat_id, RssSubscription.enabled.is_(True)))
        .order_by(RssSubscription.created_at.desc())
    )
    return list(result.scalars().all())


async def get_user_profile(db: AsyncSession, user_id: int) -> UserProfile:
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    entity = result.scalar_one_or_none()
    if entity is not None:
        return entity
    entity = UserProfile(user_id=user_id)
    db.add(entity)
    await db.commit()
    await db.refresh(entity)
    return entity


async def update_user_profile(
    db: AsyncSession, user_id: int, bio: str | None = None, about: str | None = None
) -> UserProfile:
    entity = await get_user_profile(db, user_id)
    if bio is not None:
        entity.bio = bio
    if about is not None:
        entity.about = about
    await db.commit()
    await db.refresh(entity)
    return entity


async def list_all_rss_subscriptions(db: AsyncSession) -> list[RssSubscription]:
    result = await db.execute(
        select(RssSubscription).where(RssSubscription.enabled.is_(True)).order_by(RssSubscription.created_at.asc())
    )
    return list(result.scalars().all())


async def update_rss_last_entry(db: AsyncSession, subscription_id: int, entry_id: str, title: str = "") -> None:
    result = await db.execute(select(RssSubscription).where(RssSubscription.id == subscription_id))
    entity = result.scalar_one_or_none()
    if entity is None:
        return
    entity.last_entry_id = entry_id
    if title:
        entity.title = title[:255]
    await db.commit()
