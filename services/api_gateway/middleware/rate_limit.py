import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple

class RateLimitExceededError(Exception):
    pass

# Extremely simplified in-memory token bucket for the artifact.
# Real deployment would use Redis (shared/caching) with a sliding window LUA script.
class MockRateLimiter:
    def __init__(self):
        # ip -> (tokens, last_refill)
        self.anonymous_buckets: Dict[str, Tuple[float, float]] = {}
        # user_id -> (tokens, last_refill)
        self.auth_buckets: Dict[str, Tuple[float, float]] = {}
        
    def check_limit(self, key: str, is_auth: bool):
        now = time.time()
        
        # 100 req/min anon, 1000 req/min auth
        capacity = 1000 if is_auth else 100
        refill_rate = capacity / 60.0
        
        buckets = self.auth_buckets if is_auth else self.anonymous_buckets
        
        tokens, last_refill = buckets.get(key, (capacity, now))
        
        # Refill
        time_passed = now - last_refill
        tokens = min(capacity, tokens + time_passed * refill_rate)
        
        if tokens < 1:
            raise RateLimitExceededError()
            
        # Consume
        buckets[key] = (tokens - 1, now)

limiter = MockRateLimiter()

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Very naive user extraction for artifact - real one parses JWT properly
        auth_header = request.headers.get("Authorization", "")
        
        try:
            if auth_header.startswith("Bearer "):
                # Authenticated request
                user_id = auth_header.split(" ")[1] # mocking token as user_id for simplicity
                limiter.check_limit(user_id, is_auth=True)
            else:
                # Anonymous request
                ip = request.client.host if request.client else "unknown"
                limiter.check_limit(ip, is_auth=False)
        except RateLimitExceededError:
            return Response("Too Many Requests", status_code=429)
            
        return await call_next(request)
