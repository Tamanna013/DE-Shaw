import redis.asyncio as redis
from services.auth.application.ports import TokenStorePort
from services.auth.domain.value_objects import Email
from shared.config import settings

class RedisTokenStore(TokenStorePort):
    def __init__(self, redis_client: redis.Redis): # type: ignore
        self.redis = redis_client

    async def block_refresh_token(self, jti: str, ttl_seconds: int) -> None:
        await self.redis.setex(f"blocked_token:{jti}", ttl_seconds, "1")

    async def is_refresh_token_blocked(self, jti: str) -> bool:
        return await self.redis.exists(f"blocked_token:{jti}") > 0

    async def record_failed_login(self, email: Email) -> int:
        key = f"failed_login:{email.address}"
        attempts = await self.redis.incr(key)
        if attempts == 1:
            await self.redis.expire(key, 900) # 15 minutes window
        return attempts

    async def get_failed_logins(self, email: Email) -> int:
        key = f"failed_login:{email.address}"
        attempts = await self.redis.get(key)
        return int(attempts) if attempts else 0

    async def clear_failed_logins(self, email: Email) -> None:
        key = f"failed_login:{email.address}"
        await self.redis.delete(key)
