from collections.abc import AsyncIterator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from novel_translate.api.deps import get_session
from novel_translate.api.main import app
from novel_translate.core.config import get_settings
from novel_translate.db.base import Base
from novel_translate.modules.projects import models as _models  # noqa: F401  # register tables on Base.metadata

TEST_DB_NAME = "novel_translate_test"


def _test_database_url() -> str:
    return (
        make_url(get_settings().database_url)
        .set(database=TEST_DB_NAME)
        .render_as_string(hide_password=False)
    )


async def _ensure_test_database() -> None:
    # CREATE DATABASE cannot run inside a transaction block, so use an AUTOCOMMIT
    # admin connection against the maintenance `postgres` database.
    admin_url = make_url(get_settings().database_url).set(database="postgres")
    admin_engine = create_async_engine(
        admin_url.render_as_string(hide_password=False),
        isolation_level="AUTOCOMMIT",
        poolclass=NullPool,
    )
    try:
        async with admin_engine.connect() as connection:
            already_present = await connection.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": TEST_DB_NAME},
            )
            if not already_present:
                await connection.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
    finally:
        await admin_engine.dispose()


@pytest_asyncio.fixture
async def db_engine() -> AsyncIterator[AsyncEngine]:
    # Contract: each test starts against an empty schema in its own NullPool engine.
    # Isolation is by TRUNCATE-before-test, never DROP TABLE — DROP needs an ACCESS
    # EXCLUSIVE lock that deadlocks against any still-open request/worker connection,
    # and that lock wait was a silent suite hang. create_all is idempotent (checkfirst),
    # so it only builds the schema the first time against a fresh database.
    await _ensure_test_database()
    engine = create_async_engine(_test_database_url(), poolclass=NullPool)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        await connection.execute(
            text("TRUNCATE TABLE segments, chapters, projects RESTART IDENTITY CASCADE")
        )
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
def session_factory(db_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    # Exposed so worker-task tests can build their own sessions on the same test engine
    # (the worker runs outside any request, with its own session per job).
    return async_sessionmaker(db_engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    async def _override_get_session() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_session] = _override_get_session
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://testserver") as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
