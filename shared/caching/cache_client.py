import json
import asyncio
from typing import Any, Optional, Callable, Awaitable
from redis.asyncio import Redis
from shared.caching.distributed_lock import DistributedLock, DistributedLockAcquisitionError
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class CacheClient:
    def __init__(self, redis: Redis, default_ttl: int = 3600):
        self.redis = redis
        self.default_ttl = default_ttl

    def _serialize(self, value: Any) -> str:
        return json.dumps(value)

    def _deserialize(self, value: str) -> Any:
        return json.loads(value)

    async def get(self, key: str) -> Optional[Any]:
        val = await self.redis.get(key)
        if val is None:
            return None
        try:
            return self._deserialize(val)
        except Exception as e:
            logger.error(f"Cache deserialization failed for key {key}", exc_info=e)
            return None

    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        ttl = ttl if ttl is not None else self.default_ttl
        try:
            serialized = self._serialize(value)
            return await self.redis.set(key, serialized, ex=ttl)
        except Exception as e:
            logger.error(f"Cache set failed for key {key}", exc_info=e)
            return False

    async def delete(self, key: str) -> bool:
        try:
            return bool(await self.redis.delete(key))
        except Exception as e:
            logger.error(f"Cache delete failed for key {key}", exc_info=e)
            return False

    async def get_or_set(
        self, 
        key: str, 
        compute_func: Callable[[], Awaitable[Any]], 
        ttl: int = None,
        lock_ttl_ms: int = 5000,
        lock_retry_delay_ms: int = 50,
        lock_max_retries: int = 60 # wait up to 3 seconds for stampede lock
    ) -> Any:
        """
        Stampede protection:
        1. Attempt GET. If hit, return.
        2. If miss, acquire a distributed lock specific to this key computation.
        3. Once lock acquired, GET again (another worker might have computed it while we waited).
        4. If still miss, compute, SET, and return.
        """
        val = await self.get(key)
        if val is not None:
            return val

        # Cache Miss. Protect computation against stampede.
        lock = DistributedLock(
            self.redis, 
            key=f"compute:{key}", 
            ttl_ms=lock_ttl_ms, 
            retry_delay_ms=lock_retry_delay_ms, 
            max_retries=lock_max_retries
        )
        
        try:
            async with lock:
                # Double check pattern
                val = await self.get(key)
                if val is not None:
                    return val
                    
                # Compute
                val = await compute_func()
                
                # Set
                await self.set(key, val, ttl)
                return val
        except DistributedLockAcquisitionError:
            # If we couldn't get the lock, the computation is either taking a very long time
            # or the lock is stuck. Fallback to just computing it directly to serve the request.
            logger.warning(f"Failed to acquire stampede lock for {key}, computing synchronously as fallback.")
            val = await compute_func()
            await self.set(key, val, ttl)
            return val
