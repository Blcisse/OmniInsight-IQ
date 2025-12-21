from functools import lru_cache
from typing import List, Optional
import os

try:
    from pydantic import BaseSettings, AnyHttpUrl
except Exception:  # Fallback if pydantic not installed; minimal shim
    class BaseSettings:  # type: ignore
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    AnyHttpUrl = str  # type: ignore


class Settings(BaseSettings):
    # ---------------------------------------------------
    # API / ENVIRONMENT CONFIG
    # ---------------------------------------------------
    API_PREFIX: str = os.getenv("API_PREFIX", "/api")
    ENV: str = os.getenv("ENV", os.getenv("ENVIRONMENT", "development"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in {"1", "true", "yes", "on"}

    # ---------------------------------------------------
    # CORS / FRONTEND
    # ---------------------------------------------------
    ALLOWED_ORIGINS: List[AnyHttpUrl] = (
        os.getenv("ALLOWED_ORIGINS", "*").split(",")
        if os.getenv("ALLOWED_ORIGINS")
        else ["*"]
    )

    # ---------------------------------------------------
    # DATABASE CONFIGURATION
    # ---------------------------------------------------
    DB_HOST: Optional[str] = os.getenv("DB_HOST")
    DB_PORT: Optional[int] = int(os.getenv("DB_PORT", "5432")) if os.getenv("DB_PORT") else None
    DB_NAME: Optional[str] = os.getenv("DB_NAME")
    DB_USER: Optional[str] = os.getenv("DB_USER")
    DB_PASS: Optional[str] = os.getenv("DB_PASS")

    # Optional direct connection URLs
    PG_URI: Optional[str] = os.getenv("PG_URI")
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

    # ---------------------------------------------------
    # DATABASE URL BUILDER
    # ---------------------------------------------------
    def build_database_url(self) -> str:
        """
        Construct SQLAlchemy async database URL.
        Priority order:
          1. PG_URI (explicit)
          2. DATABASE_URL (environment)
          3. Individual parts (DB_USER, DB_PASS, etc.)
        Fallback: local default for dev/testing.
        """
        if self.PG_URI:
            return self.PG_URI.strip()
        if self.DATABASE_URL:
            return self.DATABASE_URL.strip()
        if all([self.DB_HOST, self.DB_NAME, self.DB_USER, self.DB_PASS]):
            port = self.DB_PORT or 5432
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{port}/{self.DB_NAME}"
        # Default fallback (safe local setup using SQLite for offline testing)
        return "sqlite+aiosqlite:///./test.db"


# ---------------------------------------------------
# SETTINGS ACCESSOR
# ---------------------------------------------------
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance for fast reuse."""
    return Settings()
