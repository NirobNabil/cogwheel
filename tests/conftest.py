import asyncio
import os
import sys
from collections.abc import AsyncGenerator, Callable, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

DEFAULT_TEST_DATABASE_URL = (
    "postgresql+psycopg://hospitality_test:hospitality_test@localhost:5433/hospitality_test"
)
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", DEFAULT_TEST_DATABASE_URL)
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from data.model.transaction_model import Transaction  # noqa: E402
from infrastructure.configuration.db_config import Base, get_db  # noqa: E402
from infrastructure.main import create_app  # noqa: E402


@pytest.fixture(scope="session")
def test_database_url() -> str:
    return TEST_DATABASE_URL


@pytest.fixture
def db_session_factory() -> Generator[async_sessionmaker[AsyncSession], None, None]:
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    session_factory = async_sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )

    async def recreate_tables() -> None:
        try:
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.drop_all)
                await connection.run_sync(Base.metadata.create_all)
        except OperationalError as exc:
            pytest.fail(
                "PostgreSQL test database is not available. "
                "Run tests with `docker compose -f docker-compose.test.yml run --rm tests` "
                "or set TEST_DATABASE_URL to a running PostgreSQL database. "
                f"Original error: {exc}"
            )

    asyncio.run(recreate_tables())
    try:
        yield session_factory
    finally:
        asyncio.run(engine.dispose())


@pytest.fixture
def client(db_session_factory: async_sessionmaker[AsyncSession]) -> Generator[TestClient, None, None]:
    app = create_app()

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with db_session_factory() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def count_transactions(
    db_session_factory: async_sessionmaker[AsyncSession],
) -> Callable[[], int]:
    def count() -> int:
        async def count_rows() -> int:
            async with db_session_factory() as db:
                value = await db.scalar(select(func.count()).select_from(Transaction))
                return int(value or 0)

        return asyncio.run(count_rows())

    return count


@pytest.fixture
def get_transactions(
    db_session_factory: async_sessionmaker[AsyncSession],
) -> Callable[[], list[Transaction]]:
    def fetch() -> list[Transaction]:
        async def fetch_rows() -> list[Transaction]:
            async with db_session_factory() as db:
                result = await db.scalars(select(Transaction).order_by(Transaction.id.asc()))
                return list(result.all())

        return asyncio.run(fetch_rows())

    return fetch
