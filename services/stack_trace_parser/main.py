from fastapi import FastAPI
from services.stack_trace_parser.interfaces.api.router import router as trace_router
from shared.logging_engine import configure_logging, LoggingMiddleware

configure_logging(env="prod", module_name="stack_trace_parser")

app = FastAPI(
    title="TestLens Stack Trace Parser API",
    description="Parses stack traces from multiple languages, normalizes them, and optionally enriches with source code context.",
    version="1.0.0"
)

app.add_middleware(LoggingMiddleware)
app.include_router(trace_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
