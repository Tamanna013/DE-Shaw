from fastapi import APIRouter, Response
from typing import Dict, Any

router = APIRouter(tags=["health"])

# Mock dependencies
async def check_db() -> bool:
    return True
    
async def check_redis() -> bool:
    return True

@router.get("/healthz", response_model=Dict[str, str])
async def healthz():
    """Liveness probe. Returns 200 immediately if the app is running."""
    return {"status": "ok"}

@router.get("/readyz")
async def readyz(response: Response):
    """
    Readiness probe. Checks downstream dependencies (DB, Redis).
    If a dependency is unreachable, returns 503 so orchestrators stop routing traffic.
    """
    db_ok = await check_db()
    redis_ok = await check_redis()
    
    if not db_ok or not redis_ok:
        response.status_code = 503
        return {
            "status": "error", 
            "dependencies": {
                "db": "ok" if db_ok else "unreachable",
                "redis": "ok" if redis_ok else "unreachable"
            }
        }
        
    return {"status": "ok", "dependencies": {"db": "ok", "redis": "ok"}}
