import re

DEFAULT_AD_REGEX = r"(t\.me/|telegram\.me/|vx|wechat|free|bet|promo)"


class AdBlockGuard:
    def __init__(self) -> None:
        self._last_pattern = ""
        self._compiled = re.compile(DEFAULT_AD_REGEX, re.IGNORECASE)

    def is_ad(self, text: str, pattern: str) -> bool:
        if pattern != self._last_pattern:
            try:
                self._compiled = re.compile(pattern, re.IGNORECASE)
                self._last_pattern = pattern
            except re.error:
                self._compiled = re.compile(DEFAULT_AD_REGEX, re.IGNORECASE)
                self._last_pattern = DEFAULT_AD_REGEX
        return bool(text and self._compiled.search(text))
