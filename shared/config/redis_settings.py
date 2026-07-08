from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr

class RedisSettings(BaseSettings):
    """
    Settings required for services that connect to Redis (Caching, Locks, Celery).
    """
    REDIS_URL: SecretStr = Field(..., description="Redis connection URL (redis://...)")
    REDIS_POOL_MAX_CONNECTIONS: int = Field(default=50, description="Max connections for redis.asyncio pool")
