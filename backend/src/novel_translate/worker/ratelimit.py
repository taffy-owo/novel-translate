import asyncio
import time
from collections import deque


class AsyncRateLimiter:
    """Sliding-window async rate limiter.

    Allows at most `rpm` acquisitions within any `window`-second span. Contract: a single
    shared instance throttles all concurrent callers (the worker stores one in its context
    and every translation job awaits acquire() before calling the model), so the process
    stays within the provider's per-minute request cap. acquire() returns immediately when a
    slot is free and otherwise sleeps until the oldest in-window call expires.
    """

    def __init__(self, rpm: int, window: float = 60.0) -> None:
        self._max_calls = max(1, rpm)
        self._window = window
        self._calls: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            while True:
                now = time.monotonic()
                while self._calls and now - self._calls[0] >= self._window:
                    self._calls.popleft()
                if len(self._calls) < self._max_calls:
                    self._calls.append(now)
                    return
                await asyncio.sleep(self._window - (now - self._calls[0]))
