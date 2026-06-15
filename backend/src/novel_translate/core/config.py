from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://novel:novel@127.0.0.1:5432/novel_translate"
    redis_url: str = "redis://127.0.0.1:6379/0"
    minio_endpoint: str = "http://127.0.0.1:9000"
    minio_access_key: str = "novel"
    minio_secret_key: str = "novel_password"
    minio_bucket: str = "novel-translate"
    nt_provider_kind: str = "openai_compatible"
    openai_base_url: str | None = "http://127.0.0.1:11434/v1"
    openai_api_key: str | None = None
    openai_model: str | None = None
    anthropic_api_key: str | None = None
    anthropic_model: str | None = "claude-sonnet-4-6"
    provider_rpm: int = 20  # 翻译模型每分钟请求上限（worker 限流，遵守供应商速率）

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
