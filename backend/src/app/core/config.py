from functools import lru_cache
from typing import List, Optional
import logging
import os
from pathlib import Path

# Load .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass  # python-dotenv not installed, will use existing env vars

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
    # FRONTEND PROXY CONTRACT
    # ---------------------------------------------------
    FRONTEND_PROXY_ENABLED: bool = (
        os.getenv("INSIGHTOPS_FRONTEND_PROXY_ENABLED", "true").lower() in {"1", "true", "yes", "on"}
    )

    # ---------------------------------------------------
    # DATABASE URL BUILDER
    # ---------------------------------------------------
    def build_database_url(self) -> Optional[str]:
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
        return None

    # ---------------------------------------------------
    # STARTUP WARNINGS (non-fatal)
    # ---------------------------------------------------
    def startup_warnings(self) -> List[str]:
        warnings: List[str] = []
        has_pg_env = any([self.PG_URI, self.DATABASE_URL, self.DB_HOST, self.DB_NAME, self.DB_USER, self.DB_PASS])
        if not has_pg_env:
            warnings.append(
                "DATABASE_URL not set; DB features disabled until configured."
            )

        if self.ENV.lower() in {"dev", "development"} and not self.FRONTEND_PROXY_ENABLED:
            warnings.append(
                "Running in development without frontend proxy enabled. "
                "InsightOps frontend calls must go through /api/insightops/* proxy routes."
            )

        return warnings


def emit_startup_warnings(settings: Settings) -> None:
    logger = logging.getLogger("uvicorn")
    for warning in settings.startup_warnings():
        logger.warning(warning)


# ---------------------------------------------------
# SETTINGS ACCESSOR
# ---------------------------------------------------
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance for fast reuse."""
    settings = Settings()
    emit_startup_warnings(settings)
    return settings
