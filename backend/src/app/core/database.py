from __future__ import annotations

import os
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from .config import get_settings


# ---------------------------------------------------------
# 1. Load Environment Settings and Build Database URL
# ---------------------------------------------------------
settings = get_settings()
DATABASE_URL: Optional[str] = settings.build_database_url() if hasattr(settings, "build_database_url") else None
RUNNING_TESTS = "PYTEST_CURRENT_TEST" in os.environ
DB_LOCKED_FOR_TESTS = RUNNING_TESTS and not DATABASE_URL

if not DATABASE_URL:
    import logging

    logger = logging.getLogger("uvicorn")
    logger.warning("DATABASE_URL not set; DB features disabled until configured.")


# ---------------------------------------------------------
# 2. Async Engine Setup
# ---------------------------------------------------------
engine = None
async_engine = None
AsyncSessionLocal = None

# Prevent accidental DB usage in unit tests without a configured database.
if DATABASE_URL and not DB_LOCKED_FOR_TESTS:
    # Enable NullPool during tests to avoid asyncpg concurrency issues.
    use_null_pool = os.getenv("SQLALCHEMY_NULLPOOL", "false").lower() in {"1", "true", "yes", "on"}

    engine = create_async_engine(
        DATABASE_URL,
        echo=os.getenv("SQLALCHEMY_ECHO", "false").lower() in {"1", "true", "yes", "on"},
        future=True,
        poolclass=NullPool if use_null_pool else None,
    )
    async_engine = engine  # backward compatibility for tests referencing async_engine

    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


# ---------------------------------------------------------
# 3. Declarative Base
# ---------------------------------------------------------
Base = declarative_base()


# ---------------------------------------------------------
# 4. Helpers
# ---------------------------------------------------------
def _raise_db_disabled() -> None:
    raise RuntimeError("DATABASE_URL not set (DB access disabled during unit tests).")


def get_engine_or_raise():
    if engine is None or DB_LOCKED_FOR_TESTS:
        _raise_db_disabled()
    return engine


# ---------------------------------------------------------
# 5. Dependency for FastAPI Routes (yields AsyncSession)
# ---------------------------------------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yields an AsyncSession for FastAPI routes, ensuring closure."""
    if AsyncSessionLocal is None or DB_LOCKED_FOR_TESTS:
        _raise_db_disabled()
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
    For production, prefer managed migration scripts.
    """
    # Import models to register them with Base metadata
    from ..models import Base as _Base  # noqa: F401
    from ..models import (  # noqa: F401
        SaleORM,
        CampaignORM,
        ConversionORM,
        ProductORM,
        UserORM,
        IoKpiDailyORM,
        IoEngagementSignalDailyORM,
        IoExecSummaryORM,
    )

    async with get_engine_or_raise().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
