from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr

class DatabaseSettings(BaseSettings):
    """
    Settings required for services that connect to PostgreSQL.
    """
    # Use SecretStr to prevent raw DB credentials from ever hitting logs
    DATABASE_URL: SecretStr = Field(..., description="Asyncpg database URL (postgresql+asyncpg://...)")
    DB_POOL_SIZE: int = Field(default=10, description="SQLAlchemy async engine pool size")
    DB_MAX_OVERFLOW: int = Field(default=20, description="SQLAlchemy async engine max overflow")
    DB_ECHO: bool = Field(default=False, description="Enable SQLAlchemy raw SQL echoing (dev only)")
