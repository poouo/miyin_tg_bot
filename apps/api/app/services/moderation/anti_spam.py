from collections import defaultdict, deque
from time import time

from packages.shared.shared.config.settings import settings


class AntiSpamGuard:
    def __init__(self, window_sec: int | None = None, max_messages: int | None = None) -> None:
        self.window_sec = window_sec or settings.spam_window_sec
        self.max_messages = max_messages or settings.spam_max_messages
        self._bucket: dict[tuple[int, int], deque[float]] = defaultdict(deque)

    def hit(self, chat_id: int, user_id: int) -> bool:
        key = (chat_id, user_id)
        now = time()
        queue = self._bucket[key]
        queue.append(now)

        while queue and now - queue[0] > self.window_sec:
            queue.popleft()

        return len(queue) > self.max_messages

