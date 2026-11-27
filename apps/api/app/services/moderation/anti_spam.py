from collections import defaultdict, deque
from time import monotonic


class AntiSpamGuard:
    def __init__(self) -> None:
        self._bucket: dict[tuple[int, int], deque[tuple[float, str]]] = defaultdict(deque)
        self._prune_at = 0.0

    def hit(
        self,
        chat_id: int,
        user_id: int,
        text: str,
        window_sec: int,
        same_text_max: int,
        different_text_max: int,
        *,
        global_window_sec: int | None = None,
        global_max_messages: int | None = None,
    ) -> bool:
        key = (chat_id, user_id)
        now = monotonic()
        if now >= self._prune_at:
            self._prune_at = now + 60
            self._bucket = defaultdict(deque, {
                key: messages for key, messages in self._bucket.items() if now - messages[-1][0] <= 120
            })
        normalized_text = " ".join((text or "").split()).lower()
        queue = self._bucket[key]
        queue.append((now, normalized_text))

        retention = max(window_sec, global_window_sec or 0)
        while queue and now - queue[0][0] > retention:
            queue.popleft()

        local = [item for timestamp, item in queue if now - timestamp <= window_sec]
        global_count = sum(now - timestamp <= global_window_sec for timestamp, _ in queue) if global_window_sec else 0
        return (
            local.count(normalized_text) >= same_text_max
            or len(set(local)) >= different_text_max
            or (global_max_messages is not None and global_count >= global_max_messages)
        )
