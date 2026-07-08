import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from shared.logging_engine import set_trace_id

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Look for incoming trace ID from upstream proxy, or generate new
        request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        
        # Bind to our shared logging engine context
        set_trace_id(request_id)
        
        # Attach to request state for downstream routers
        request.state.request_id = request_id
        
        response = await call_next(request)
        
        # Guarantee it's in the response headers
        response.headers["X-Request-Id"] = request_id
        return response
