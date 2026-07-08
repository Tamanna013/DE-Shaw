import asyncio
import uuid
import logging
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

# Lua script to safely release a lock only if the token matches.
# Returns 1 if released, 0 if token mismatch or key missing.
RELEASE_LUA = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
"""

class DistributedLockError(Exception):
    pass

class DistributedLockAcquisitionError(DistributedLockError):
    pass

class DistributedLock:
    def __init__(self, redis: Redis, key: str, ttl_ms: int = 30000, retry_delay_ms: int = 100, max_retries: int = 0):
        self.redis = redis
        self.key = f"testlens:lock:{key}"
        self.ttl_ms = ttl_ms
        self.retry_delay = retry_delay_ms / 1000.0
        self.max_retries = max_retries
        self.token = str(uuid.uuid4())
        self._acquired = False
        # Register Lua script
        self._release_script = self.redis.register_script(RELEASE_LUA)

    async def acquire(self) -> bool:
        retries = 0
        while retries <= self.max_retries:
            # SET NX PX
            result = await self.redis.set(self.key, self.token, nx=True, px=self.ttl_ms)
            if result:
                self._acquired = True
                return True
                
            if self.max_retries > 0:
                await asyncio.sleep(self.retry_delay)
                retries += 1
            else:
                break
                
        return False

    async def release(self) -> bool:
        if not self._acquired:
            return False
            
        try:
            res = await self._release_script(keys=[self.key], args=[self.token])
            self._acquired = False
            return bool(res)
        except Exception as e:
            logger.error(f"Failed to release distributed lock for key {self.key}: {e}")
            return False

    async def __aenter__(self):
        acquired = await self.acquire()
        if not acquired:
            raise DistributedLockAcquisitionError(f"Failed to acquire lock for key {self.key}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.release()
