from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

# We define dummy exception classes here that represent the Domain exceptions
# from the various sub-modules (since we don't have them all physically installed in this artifact's env)
class AuthenticationError(Exception): pass
class AuthorizationError(Exception): pass
class NotFoundError(Exception): pass
class ConflictError(Exception): pass
class RateLimitExceededError(Exception): pass
class DomainValidationError(Exception): pass

# Generic envelope generator
def _error_response(request: Request, status_code: int, code: str, message: str) -> JSONResponse:
    trace_id = getattr(request.state, "request_id", "unknown")
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "trace_id": trace_id
            }
        }
    )

def setup_exception_handlers(app: FastAPI):
    logger = logging.getLogger("gateway.exceptions")

    @app.exception_handler(AuthenticationError)
    async def auth_handler(request: Request, exc: AuthenticationError):
        return _error_response(request, 401, "UNAUTHORIZED", str(exc))

    @app.exception_handler(AuthorizationError)
    async def authz_handler(request: Request, exc: AuthorizationError):
        return _error_response(request, 403, "FORBIDDEN", str(exc))

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return _error_response(request, 404, "NOT_FOUND", str(exc))

    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError):
        return _error_response(request, 409, "CONFLICT", str(exc))

    @app.exception_handler(DomainValidationError)
    async def domain_validation_handler(request: Request, exc: DomainValidationError):
        return _error_response(request, 422, "VALIDATION_ERROR", str(exc))

    @app.exception_handler(RateLimitExceededError)
    async def rate_limit_handler(request: Request, exc: RateLimitExceededError):
        return _error_response(request, 429, "RATE_LIMIT_EXCEEDED", "Too many requests. Please try again later.")

    @app.exception_handler(RequestValidationError)
    async def fastapi_validation_handler(request: Request, exc: RequestValidationError):
        # Pydantic validation errors on the request payload
        return _error_response(request, 422, "VALIDATION_ERROR", "Invalid request format.")

    @app.exception_handler(Exception)
    async def global_handler(request: Request, exc: Exception):
        # Global catch-all for unhandled 500s. NEVER leak internal details.
        trace_id = getattr(request.state, "request_id", "unknown")
        logger.error(f"Unhandled Server Error [trace_id={trace_id}]", exc_info=exc)
        return _error_response(
            request, 
            500, 
            "INTERNAL_SERVER_ERROR", 
            "An unexpected error occurred. Please contact support if the issue persists."
        )
