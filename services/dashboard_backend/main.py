from fastapi import FastAPI
from services.dashboard_backend.interfaces.api.router import router as dashboard_router
from shared.logging_engine import configure_logging, LoggingMiddleware

configure_logging(env="prod", module_name="dashboard_backend")

app = FastAPI(
    title="TestLens Dashboard API",
    description="Serves aggregated, query-optimized metrics and trends.",
    version="1.0.0"
)

app.add_middleware(LoggingMiddleware)
app.include_router(dashboard_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
