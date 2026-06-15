from collections.abc import AsyncIterator

from arq.connections import ArqRedis

from novel_translate.core.db import get_session
from novel_translate.core.redis import create_arq_pool

__all__ = ["get_session", "get_arq_pool"]


async def get_arq_pool() -> AsyncIterator[ArqRedis]:
    pool = await create_arq_pool()
    try:
        yield pool
    finally:
        await pool.close()
