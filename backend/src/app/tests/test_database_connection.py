import asyncio
from src.app.core.database import async_engine

async def test_connection():
    async with async_engine.begin() as conn:
        result = await conn.run_sync(lambda c: c.execute("SELECT 1"))
        print("✅ Database connection successful:", result)

if __name__ == "__main__":
    asyncio.run(test_connection())
