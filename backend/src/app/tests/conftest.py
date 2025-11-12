import asyncio
import os
import pytest

from src.app.core.database import engine, Base, AsyncSessionLocal

# Ensure NullPool for testing to avoid asyncpg concurrency issues
os.environ["SQLALCHEMY_NULLPOOL"] = "true"

@pytest.fixture(scope="session")
def event_loop():
    """Create a single session-wide event loop for all async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def db_setup():
    """Create all tables once per test session, drop at end."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
