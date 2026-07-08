from fastapi import FastAPI
from services.api_gateway.middleware.cors import setup_cors
from services.api_gateway.middleware.rate_limit import RateLimitMiddleware
from services.api_gateway.middleware.request_id import RequestIdMiddleware
from services.api_gateway.exception_handlers import setup_exception_handlers
from services.api_gateway.health import router as health_router

# In reality we would import routers from the actual service modules:
# from services.auth.interfaces.api.router import router as auth_router
# from services.failure_analyzer.interfaces.api.router import router as failure_router

app = FastAPI(
    title="TestLens API",
    description="Unified API Gateway for the TestLens Platform.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 1. Setup CORS
setup_cors(app)

# 2. Add Middlewares (Order matters: outermost first in execution)
# Request ID injected first so logging works
app.add_middleware(RequestIdMiddleware)
# Rate limit checked before routing
app.add_middleware(RateLimitMiddleware)

# 3. Setup Global Exception Handlers
setup_exception_handlers(app)

# 4. Include Routers
app.include_router(health_router)
# app.include_router(auth_router)
# app.include_router(failure_router)

# Dummy endpoint for testing exception mapping in the artifact
@app.get("/api/v1/trigger-error")
async def trigger_error(type: str = "internal"):
    from services.api_gateway.exception_handlers import (
        AuthenticationError, AuthorizationError, NotFoundError, 
        ConflictError, DomainValidationError
    )
    
    if type == "auth": raise AuthenticationError("Invalid token")
    if type == "authz": raise AuthorizationError("Insufficient permissions")
    if type == "notfound": raise NotFoundError("Resource missing")
    if type == "conflict": raise ConflictError("Resource exists")
    if type == "validation": raise DomainValidationError("Invalid data")
    
    # Generic unhandled
    raise ValueError("Something unexpected broke")
