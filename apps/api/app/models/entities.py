from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from apps.api.app.models.base import Base, TimestampMixin


class GroupConfig(Base, TimestampMixin):
    __tablename__ = "group_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255), default="")

    join_verification_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    keyword_filter_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    ad_block_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_spam_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_recover_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    deepseek_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    join_verify_fail_action: Mapped[str] = mapped_column(String(32), default="kick")
    join_verify_fail_kick_minutes: Mapped[int] = mapped_column(Integer, default=1)
    join_verify_fail_mute_minutes: Mapped[int] = mapped_column(Integer, default=30)
    join_verify_fail_ban_minutes: Mapped[int] = mapped_column(Integer, default=1440)
    ad_block_action: Mapped[str] = mapped_column(String(32), default="mute")
    ad_block_delete_message: Mapped[bool] = mapped_column(Boolean, default=True)
    ad_block_kick_minutes: Mapped[int] = mapped_column(Integer, default=1)
    ad_block_mute_minutes: Mapped[int] = mapped_column(Integer, default=30)
    ad_block_ban_minutes: Mapped[int] = mapped_column(Integer, default=1440)
    anti_spam_action: Mapped[str] = mapped_column(String(32), default="mute")
    anti_spam_delete_message: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_spam_window_sec: Mapped[int] = mapped_column(Integer, default=10)
    anti_spam_same_text_max: Mapped[int] = mapped_column(Integer, default=3)
    anti_spam_different_text_max: Mapped[int] = mapped_column(Integer, default=6)
    anti_spam_kick_minutes: Mapped[int] = mapped_column(Integer, default=1)
    anti_spam_mute_minutes: Mapped[int] = mapped_column(Integer, default=30)
    anti_spam_ban_minutes: Mapped[int] = mapped_column(Integer, default=1440)


class KeywordRule(Base, TimestampMixin):
    __tablename__ = "keyword_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    keyword: Mapped[str] = mapped_column(String(255), index=True)
    action: Mapped[str] = mapped_column(String(32), default="delete")
    mute_minutes: Mapped[int] = mapped_column(Integer, default=10)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class AutoReplyRule(Base, TimestampMixin):
    __tablename__ = "auto_reply_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    keyword: Mapped[str] = mapped_column(String(255), index=True)
    reply_text: Mapped[str] = mapped_column(Text, default="")
    parse_mode: Mapped[str] = mapped_column(String(16), default="plain")
    delete_after_seconds: Mapped[int] = mapped_column(Integer, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class AdKeyword(Base, TimestampMixin):
    __tablename__ = "ad_keywords"
    __table_args__ = (UniqueConstraint("chat_id", "keyword", name="uq_ad_keyword_chat_keyword"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    keyword: Mapped[str] = mapped_column(String(255), index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class ModerationLog(Base):
    __tablename__ = "moderation_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    username: Mapped[str] = mapped_column(String(255), default="")
    event_type: Mapped[str] = mapped_column(String(64))
    detail: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class VerificationChallenge(Base):
    __tablename__ = "verification_challenges"
    __table_args__ = (UniqueConstraint("chat_id", "user_id", name="uq_chat_user_challenge"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    question: Mapped[str] = mapped_column(String(255))
    answer: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    passed: Mapped[bool] = mapped_column(Boolean, default=False)


class UserSanction(Base, TimestampMixin):
    __tablename__ = "user_sanctions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    sanction_type: Mapped[str] = mapped_column(String(32), default="mute")
    reason: Mapped[str] = mapped_column(String(255), default="")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    recovered: Mapped[bool] = mapped_column(Boolean, default=False)


class RulesConfig(Base, TimestampMixin):
    __tablename__ = "rules_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    rules_text: Mapped[str] = mapped_column(Text, default="")


class NoteRule(Base, TimestampMixin):
    __tablename__ = "note_rules"
    __table_args__ = (UniqueConstraint("chat_id", "name", name="uq_note_chat_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    name: Mapped[str] = mapped_column(String(64), index=True)
    text: Mapped[str] = mapped_column(Text, default="")
    parse_mode: Mapped[str] = mapped_column(String(16), default="plain")


class WarningSetting(Base, TimestampMixin):
    __tablename__ = "warning_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    warn_limit: Mapped[int] = mapped_column(Integer, default=3)
    warn_action: Mapped[str] = mapped_column(String(32), default="mute")
    mute_minutes: Mapped[int] = mapped_column(Integer, default=60)
    ban_minutes: Mapped[int] = mapped_column(Integer, default=1440)


class UserWarning(Base, TimestampMixin):
    __tablename__ = "user_warnings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    admin_id: Mapped[int] = mapped_column(BigInteger, default=0)
    reason: Mapped[str] = mapped_column(Text, default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class ReportConfig(Base, TimestampMixin):
    __tablename__ = "report_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class LockConfig(Base, TimestampMixin):
    __tablename__ = "lock_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    links: Mapped[bool] = mapped_column(Boolean, default=False)
    forwards: Mapped[bool] = mapped_column(Boolean, default=False)
    media: Mapped[bool] = mapped_column(Boolean, default=False)
    stickers: Mapped[bool] = mapped_column(Boolean, default=False)
    commands: Mapped[bool] = mapped_column(Boolean, default=False)


class WelcomeConfig(Base, TimestampMixin):
    __tablename__ = "welcome_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    welcome_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    goodbye_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    clean_welcome: Mapped[bool] = mapped_column(Boolean, default=True)
    welcome_text: Mapped[str] = mapped_column(Text, default="欢迎 {fullname} 加入 {chat_title}。")
    goodbye_text: Mapped[str] = mapped_column(Text, default="{fullname} 离开了 {chat_title}。")
    last_welcome_message_id: Mapped[int] = mapped_column(Integer, default=0)


class LogChannelConfig(Base, TimestampMixin):
    __tablename__ = "log_channel_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    log_chat_id: Mapped[int] = mapped_column(BigInteger, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)


class GlobalBan(Base, TimestampMixin):
    __tablename__ = "global_bans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    reason: Mapped[str] = mapped_column(Text, default="")
    admin_id: Mapped[int] = mapped_column(BigInteger, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class DisabledCommand(Base, TimestampMixin):
    __tablename__ = "disabled_commands"
    __table_args__ = (UniqueConstraint("chat_id", "command", name="uq_disabled_command_chat_command"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    command: Mapped[str] = mapped_column(String(64), index=True)


class AfkStatus(Base, TimestampMixin):
    __tablename__ = "afk_statuses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    reason: Mapped[str] = mapped_column(Text, default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class RssSubscription(Base, TimestampMixin):
    __tablename__ = "rss_subscriptions"
    __table_args__ = (UniqueConstraint("chat_id", "url", name="uq_rss_chat_url"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    url: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(String(255), default="")
    last_entry_id: Mapped[str] = mapped_column(Text, default="")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class UserProfile(Base, TimestampMixin):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    bio: Mapped[str] = mapped_column(Text, default="")
    about: Mapped[str] = mapped_column(Text, default="")


class SecurityConfig(Base, TimestampMixin):
    __tablename__ = "security_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    login_ban_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    login_max_attempts: Mapped[int] = mapped_column(Integer, default=5)
    login_ban_minutes: Mapped[int] = mapped_column(Integer, default=5)


class LoginAttempt(Base, TimestampMixin):
    __tablename__ = "login_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ip: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    fail_count: Mapped[int] = mapped_column(Integer, default=0)
    banned_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AppSetting(Base, TimestampMixin):
    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    value: Mapped[str] = mapped_column(Text, default="")
