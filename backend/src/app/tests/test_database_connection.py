import pytest
from sqlalchemy import text
from src.app.core.database import engine

@pytest.mark.asyncio
async def test_connection(db_setup):
    """Test that we can establish a connection to the database."""
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        row = result.fetchone()
        assert row[0] == 1
        print("✅ Database connection successful")
