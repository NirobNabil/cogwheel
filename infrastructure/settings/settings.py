from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Hospitality Analytics Platform"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"
    database_url: str = (
        "postgresql+psycopg://hospitality:hospitality@localhost:5432/hospitality"
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def sync_database_url(database_url: str) -> str:
    """Return a sync-driver URL for tools such as Alembic."""
    return database_url.replace("sqlite+aiosqlite://", "sqlite+pysqlite://", 1)
