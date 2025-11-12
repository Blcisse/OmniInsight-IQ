from __future__ import annotations

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from .config import get_settings


# ---------------------------------------------------------
# 1. Load Environment Settings and Build Database URL
# ---------------------------------------------------------
settings = get_settings()
DATABASE_URL = settings.build_database_url() if hasattr(settings, "build_database_url") else None

if not DATABASE_URL:
    raise ValueError(
        "❌ DATABASE_URL could not be built. "
        "Ensure your .env or config provides valid DB credentials "
        "(PG_USER, PG_PASSWORD, PG_HOST, PG_PORT, PG_DB) or DATABASE_URL directly."
    )


# ---------------------------------------------------------
# 2. Async Engine Setup
# ---------------------------------------------------------
# Enable NullPool during tests to avoid asyncpg concurrency issues.
use_null_pool = os.getenv("SQLALCHEMY_NULLPOOL", "false").lower() in {"1", "true", "yes", "on"}

engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("SQLALCHEMY_ECHO", "false").lower() in {"1", "true", "yes", "on"},
    future=True,
    poolclass=NullPool if use_null_pool else None,
)


# ---------------------------------------------------------
# 3. Async Session Factory
# ---------------------------------------------------------
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# ---------------------------------------------------------
# 4. Declarative Base
# ---------------------------------------------------------
Base = declarative_base()


# ---------------------------------------------------------
# 5. Dependency for FastAPI Routes (yields AsyncSession)
# ---------------------------------------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yields an AsyncSession for FastAPI routes, ensuring closure."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ---------------------------------------------------------
# 6. Create All Tables (for Development / Testing)
# ---------------------------------------------------------
async def create_all_tables() -> None:
    """
    Create all tables defined in Base metadata.

    This is mainly for development and testing.
    For production, prefer migrations (Alembic).
    """
    # Import models to register them with Base metadata
    from ..models import Base as _Base  # noqa: F401
    from ..models import (  # noqa: F401
        SaleORM,
        CampaignORM,
        ConversionORM,
        ProductORM,
        UserORM,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
