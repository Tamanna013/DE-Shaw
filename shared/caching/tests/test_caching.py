import pytest
import asyncio
from redis.asyncio import Redis
from shared.caching.cache_client import CacheClient
from shared.caching.distributed_lock import DistributedLock, DistributedLockAcquisitionError
from shared.caching.decorators import cached

# Requires a running Redis instance on localhost:6379 for integration tests
@pytest.fixture
async def redis():
    r = Redis(host="localhost", port=6379, db=0)
    await r.flushdb()
    yield r
    await r.flushdb()
    await r.aclose()

@pytest.fixture
def cache(redis):
    return CacheClient(redis)

@pytest.mark.asyncio
async def test_get_or_set_computes_once_under_concurrent_requests(cache):
    compute_calls = 0
    
    async def expensive_compute():
        nonlocal compute_calls
        compute_calls += 1
        await asyncio.sleep(0.1) # Simulate work
        return {"data": "computed"}
        
    # Fire 10 concurrent requests for the exact same key
    tasks = [cache.get_or_set("testlens:v1:shared:data", expensive_compute) for _ in range(10)]
    results = await asyncio.gather(*tasks)
    
    # Assert computation only happened once (stampede protection)
    assert compute_calls == 1
    
    # Assert all 10 got the correct result
    for res in results:
        assert res == {"data": "computed"}

@pytest.mark.asyncio
async def test_distributed_lock_prevents_double_acquisition(redis):
    lock1 = DistributedLock(redis, "resource-A", ttl_ms=1000, max_retries=0)
    lock2 = DistributedLock(redis, "resource-A", ttl_ms=1000, max_retries=0)
    
    # Acquire lock 1
    acquired1 = await lock1.acquire()
    assert acquired1 is True
    
    # Attempt to acquire lock 2 immediately - should fail
    acquired2 = await lock2.acquire()
    assert acquired2 is False
    
    # Release lock 1
    await lock1.release()
    
    # Attempt to acquire lock 2 again - should succeed
    acquired2 = await lock2.acquire()
    assert acquired2 is True
    await lock2.release()

@pytest.mark.asyncio
async def test_distributed_lock_safe_release_does_not_release_other_holders_lock(redis):
    lock1 = DistributedLock(redis, "resource-B", ttl_ms=100, max_retries=0)
    lock2 = DistributedLock(redis, "resource-B", ttl_ms=5000, max_retries=0)
    
    # 1. Lock 1 acquires
    await lock1.acquire()
    
    # 2. Let Lock 1 EXPIRE naturally
    await asyncio.sleep(0.15)
    
    # 3. Lock 2 acquires (it's free now due to expiry)
    assert await lock2.acquire() is True
    
    # 4. Lock 1 attempts to release (even though it already expired)
    # The Lua script MUST protect against this, otherwise Lock 1 would delete Lock 2's key!
    released1 = await lock1.release()
    assert released1 is False # Should return False because token mismatch
    
    # Lock 2 should still be holding the lock securely
    assert await redis.exists(lock2.key) == 1
    await lock2.release()

@pytest.mark.asyncio
async def test_cached_decorator_respects_ttl_and_key_builder(redis):
    client = CacheClient(redis)
    calls = 0
    
    class TestService:
        @cached(client, ttl=1, key_builder=lambda self, id: f"testlens:v1:item:{id}")
        async def get_data(self, id: str):
            nonlocal calls
            calls += 1
            return f"data-{id}"
            
    svc = TestService()
    
    # Call 1: Miss
    res1 = await svc.get_data("123")
    assert res1 == "data-123"
    assert calls == 1
    
    # Call 2: Hit
    res2 = await svc.get_data("123")
    assert res2 == "data-123"
    assert calls == 1
    
    # Call 3: Different ID (Miss)
    res3 = await svc.get_data("456")
    assert res3 == "data-456"
    assert calls == 2
    
    # Wait for TTL to expire on ID 123
    await asyncio.sleep(1.1)
    
    # Call 4: ID 123 (Miss due to TTL)
    res4 = await svc.get_data("123")
    assert res4 == "data-123"
    assert calls == 3
