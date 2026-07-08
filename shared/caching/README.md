# TestLens Shared Caching

A robust, enterprise-grade caching package built over `redis.asyncio`, providing standardized patterns for caching and distributed locking across all TestLens services.

## Core Features
1. **CacheClient**: Provides `get`, `set`, and `delete` with automatic JSON serialization/deserialization.
2. **Stampede Protection**: `get_or_set(key, compute_func)` natively protects expensive backend computations from cache stampedes. When 100 concurrent requests miss the cache for the exact same key, exactly *one* request computes the value while the other 99 wait on a distributed lock, then return the freshly cached value seamlessly.
3. **Distributed Locks**: Fully safe asynchronous distributed locks utilizing `SET NX PX` and an atomic Lua release script to guarantee a process can never accidentally release a lock belonging to another process (e.g. if their own lock expired during a GC pause).
4. **Decorator Caching**: Explicit, strictly-namespaced caching via the `@cached` decorator. The decorator forces the developer to supply a `key_builder` function rather than magically hashing arbitrary Python objects, avoiding silent cross-tenant data leaks.

## Running Tests
Tests require a local Redis instance.
```bash
docker run -p 6379:6379 -d redis
pytest shared/caching/tests/
```
