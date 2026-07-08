from fastapi import FastAPI
from services.ai_reasoning_engine.interfaces.api.router import router as reasoning_router
from shared.logging_engine import configure_logging, LoggingMiddleware

configure_logging(env="prod", module_name="ai_reasoning_engine")

app = FastAPI(
    title="TestLens AI Reasoning Engine API",
    description="Retrieval-Augmented Generation (RAG) and LLM wrappers for failure analysis.",
    version="1.0.0"
)

app.add_middleware(LoggingMiddleware)
app.include_router(reasoning_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
