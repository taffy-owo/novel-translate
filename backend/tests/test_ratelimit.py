import time

from novel_translate.worker.ratelimit import AsyncRateLimiter


async def test_rate_limiter_allows_within_capacity() -> None:
    limiter = AsyncRateLimiter(rpm=5, window=0.3)
    start = time.monotonic()
    for _ in range(5):
        await limiter.acquire()
    # 容量内（5 次 / 窗口）不应阻塞
    assert time.monotonic() - start < 0.2


async def test_rate_limiter_throttles_beyond_capacity() -> None:
    limiter = AsyncRateLimiter(rpm=2, window=0.3)
    start = time.monotonic()
    for _ in range(4):
        await limiter.acquire()
    elapsed = time.monotonic() - start
    # 前 2 次即时通过；第 3、4 次需等首个窗口滚出 -> 至少阻塞一个窗口
    assert elapsed >= 0.25
