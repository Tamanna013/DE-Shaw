from fastapi import FastAPI
from services.llm_orchestration.interfaces.api.router import router as llm_router
from shared.logging_engine import configure_logging, LoggingMiddleware

configure_logging(env="prod", module_name="llm_orchestration")

app = FastAPI(
    title="TestLens LLM Orchestration API",
    description="Provider-agnostic LLM interface with circuit breakers, retries, and cost tracking.",
    version="1.0.0"
)

app.add_middleware(LoggingMiddleware)
app.include_router(llm_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
