from collections import defaultdict, deque
from time import time


class AntiSpamGuard:
    def __init__(self) -> None:
        self._bucket: dict[tuple[int, int], deque[float]] = defaultdict(deque)

    def hit(self, chat_id: int, user_id: int, window_sec: int, max_messages: int) -> bool:
        key = (chat_id, user_id)
        now = time()
        queue = self._bucket[key]
        queue.append(now)

        while queue and now - queue[0] > window_sec:
            queue.popleft()

        return len(queue) > max_messages
