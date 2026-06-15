from typing import Any

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from novel_translate.core.config import get_settings
from novel_translate.core.redis import get_arq_redis_settings
from novel_translate.worker.ratelimit import AsyncRateLimiter
from novel_translate.worker.tasks.translate_segment import translate_segment


async def startup(ctx: dict[str, Any]) -> None:
    # The worker owns its own engine/session factory; each job opens a short-lived session.
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    ctx["engine"] = engine
    ctx["session_factory"] = async_sessionmaker(engine, expire_on_commit=False)
    # Shared limiter keeps all concurrent jobs within the provider's per-minute cap.
    ctx["rate_limiter"] = AsyncRateLimiter(settings.provider_rpm)


async def shutdown(ctx: dict[str, Any]) -> None:
    engine: AsyncEngine | None = ctx.get("engine")
    if engine is not None:
        await engine.dispose()


class WorkerSettings:
    functions = [translate_segment]
    redis_settings = get_arq_redis_settings()
    on_startup = startup
    on_shutdown = shutdown
