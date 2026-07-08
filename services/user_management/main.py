from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uuid

from services.user_management.interfaces.api.router import router as um_router
from shared.logging_engine import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="TestLens User Management API",
    description="RBAC, Teams, and User Profiles",
    version="1.0.0"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append(f"{field}: {error['msg']}")
    
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "; ".join(errors),
                "trace_id": str(uuid.uuid4())
            }
        }
    )

app.include_router(um_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
