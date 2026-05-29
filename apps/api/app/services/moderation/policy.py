from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.models.entities import KeywordRule
from apps.api.app.services.group_service import get_group
from apps.api.app.services.moderation.ad_block import AdBlockGuard
from apps.api.app.services.moderation.anti_spam import AntiSpamGuard
from apps.api.app.services.moderation.keyword_filter import match_keyword_rule
from apps.api.app.services.runtime_config_service import get_runtime_config


@dataclass
class ModerationDecision:
    blocked: bool
    reason: str = ""
    keyword_rule: KeywordRule | None = None


class ModerationPolicyEngine:
    def __init__(self) -> None:
        self.ad_guard = AdBlockGuard()
        self.spam_guard = AntiSpamGuard()

    async def check_message(self, db: AsyncSession, chat_id: int, user_id: int, text: str) -> ModerationDecision:
        config = await get_group(db, chat_id)
        if config is None:
            return ModerationDecision(blocked=False)
        runtime = await get_runtime_config(db)

        if config.ad_block_enabled and self.ad_guard.is_ad(text, runtime.ad_regex):
            return ModerationDecision(blocked=True, reason="ad_block")

        if config.keyword_filter_enabled:
            keyword_rule = await match_keyword_rule(db, chat_id, text)
            if keyword_rule:
                return ModerationDecision(blocked=True, reason="keyword_filter", keyword_rule=keyword_rule)

        if config.anti_spam_enabled and self.spam_guard.hit(
            chat_id, user_id, runtime.spam_window_sec, runtime.spam_max_messages
        ):
            return ModerationDecision(blocked=True, reason="anti_spam")

        return ModerationDecision(blocked=False)
