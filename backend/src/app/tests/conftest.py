import os
import pytest

# Ensure NullPool for testing to avoid asyncpg concurrency issues
os.environ["SQLALCHEMY_NULLPOOL"] = "true"

# Import after setting environment variable to ensure NullPool is used
from src.app.core.database import engine, Base, AsyncSessionLocal

@pytest.fixture(scope="session", autouse=True)
async def db_setup():
    """Create all tables once per test session, drop at end."""
    # Ensure tables are created before any tests run
    # Use checkfirst=False to avoid querying while other operations might be in progress
    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn, checkfirst=False))
    yield
    # Clean up after all tests complete
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session():
    """Provide a database session for each test."""
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()  # Ensure any uncommitted changes are rolled back
