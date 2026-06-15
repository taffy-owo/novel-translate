from urllib.parse import urlparse

from arq.connections import RedisSettings

from novel_translate.core.config import get_settings


def build_arq_redis_settings(redis_url: str) -> RedisSettings:
    parsed_url = urlparse(redis_url)
    redis_database = int(parsed_url.path.lstrip("/") or "0")
    redis_ssl = parsed_url.scheme == "rediss"

    return RedisSettings(
        host=parsed_url.hostname or "localhost",
        port=parsed_url.port or 6379,
        database=redis_database,
        password=parsed_url.password,
        ssl=redis_ssl,
    )


def get_arq_redis_settings() -> RedisSettings:
    return build_arq_redis_settings(get_settings().redis_url)
