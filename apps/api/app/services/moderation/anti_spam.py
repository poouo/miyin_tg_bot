from collections import defaultdict, deque
from time import time


class AntiSpamGuard:
    def __init__(self) -> None:
        self._bucket: dict[tuple[int, int], deque[tuple[float, str]]] = defaultdict(deque)

    def hit(
        self,
        chat_id: int,
        user_id: int,
        text: str,
        window_sec: int,
        same_text_max: int,
        different_text_max: int,
    ) -> bool:
        key = (chat_id, user_id)
        now = time()
        normalized_text = " ".join((text or "").split()).lower()
        queue = self._bucket[key]
        queue.append((now, normalized_text))

        while queue and now - queue[0][0] > window_sec:
            queue.popleft()

        same_text_count = 0
        for _, item in reversed(queue):
            if item != normalized_text:
                break
            same_text_count += 1
        different_text_count = len({item for _, item in queue})
        return same_text_count >= same_text_max or different_text_count >= different_text_max
