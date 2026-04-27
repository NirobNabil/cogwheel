from uuid import uuid4

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from infrastructure.settings.settings import sync_database_url


def database_url_with_search_path(database_url: str, schema_name: str) -> str:
    separator = "&" if "?" in database_url else "?"
    return f"{database_url}{separator}options=-csearch_path={schema_name}"


def create_schema(database_url: str, schema_name: str) -> None:
    engine = create_engine(sync_database_url(database_url))
    try:
        with engine.begin() as connection:
            connection.execute(text(f'CREATE SCHEMA "{schema_name}"'))
    finally:
        engine.dispose()


def drop_schema(database_url: str, schema_name: str) -> None:
    engine = create_engine(sync_database_url(database_url))
    try:
        with engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE'))
    finally:
        engine.dispose()


def test_sync_database_url_uses_sync_psycopg_for_asyncpg_urls():
    assert (
        sync_database_url("postgresql+asyncpg://user:pass@localhost:5432/app")
        == "postgresql+psycopg://user:pass@localhost:5432/app"
    )
    assert (
        sync_database_url("postgresql+psycopg://user:pass@localhost:5432/app")
        == "postgresql+psycopg://user:pass@localhost:5432/app"
    )


def test_alembic_upgrade_head_creates_transactions_table(monkeypatch, test_database_url):
    schema_name = f"migration_{uuid4().hex}"
    create_schema(test_database_url, schema_name)
    database_url = database_url_with_search_path(test_database_url, schema_name)
    monkeypatch.setenv("DATABASE_URL", database_url)

    config = Config("alembic.ini")
    try:
        command.upgrade(config, "head")

        engine = create_engine(sync_database_url(database_url))
        inspector = inspect(engine)
        assert "transactions" in inspector.get_table_names()
        columns = {column["name"] for column in inspector.get_columns("transactions")}
        assert {
            "id",
            "property_name",
            "category",
            "price",
            "quantity",
            "date",
            "created_at",
            "updated_at",
        } <= columns
    finally:
        if "engine" in locals():
            engine.dispose()
        drop_schema(test_database_url, schema_name)
