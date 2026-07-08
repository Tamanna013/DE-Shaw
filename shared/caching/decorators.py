import functools
from typing import Callable, Any
from shared.caching.cache_client import CacheClient

def cached(
    cache_client: CacheClient, 
    ttl: int, 
    key_builder: Callable[..., str]
):
    """
    Decorator for use-case-level caching.
    Requires an explicit key_builder callable that receives the exact same arguments
    as the decorated function and returns a Namespaced string key.
    
    Example:
    @cached(client, ttl=60, key_builder=lambda self, id: f"testlens:v1:service:item:{id}")
    async def get_item(self, id: str): ...
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = key_builder(*args, **kwargs)
            
            async def compute():
                return await func(*args, **kwargs)
                
            return await cache_client.get_or_set(key, compute, ttl=ttl)
        return wrapper
    return decorator
