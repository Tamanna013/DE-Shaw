from fastapi import FastAPI
from services.failure_analyzer.interfaces.api.router import router as failure_router
from shared.logging_engine import configure_logging, LoggingMiddleware

configure_logging(env="prod", module_name="failure_analyzer")

app = FastAPI(
    title="TestLens Failure Analyzer API",
    description="Central orchestrator for test failure analysis and LLM reasoning.",
    version="1.0.0"
)

app.add_middleware(LoggingMiddleware)
app.include_router(failure_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
