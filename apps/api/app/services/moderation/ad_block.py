import re

from packages.shared.shared.config.settings import settings


class AdBlockGuard:
    def __init__(self, pattern: str | None = None) -> None:
        self.pattern = re.compile(pattern or settings.ad_regex, re.IGNORECASE)

    def is_ad(self, text: str) -> bool:
        return bool(text and self.pattern.search(text))

