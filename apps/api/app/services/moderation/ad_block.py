import re


class AdBlockGuard:
    def __init__(self) -> None:
        self._last_pattern = ""
        self._compiled: re.Pattern[str] | None = None

    def is_ad(self, text: str, pattern: str) -> bool:
        pattern = (pattern or "").strip()
        if not pattern:
            self._compiled = None
            self._last_pattern = ""
            return False
        if pattern != self._last_pattern:
            try:
                self._compiled = re.compile(pattern, re.IGNORECASE)
                self._last_pattern = pattern
            except re.error:
                self._compiled = None
                self._last_pattern = ""
                return False
        return bool(text and self._compiled and self._compiled.search(text))
