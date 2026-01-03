import os
import pytest

# Ensure NullPool for testing to avoid asyncpg concurrency issues
os.environ["SQLALCHEMY_NULLPOOL"] = "true"

# Import after setting environment variable to ensure NullPool is used
from src.app.core.database import engine, Base, AsyncSessionLocal


@pytest.fixture(scope="session", autouse=True)
async def db_setup():
    """Create all tables once per test session, drop at end."""
    if engine is None:
        # No database configured; allow DB-free tests to proceed.
        yield
        return

    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn, checkfirst=False))
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session():
    """Provide a database session for each test."""
    if AsyncSessionLocal is None:
        pytest.skip("DATABASE_URL not configured; database-backed tests skipped.")
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()  # Ensure any uncommitted changes are rolled back
