from fastapi import FastAPI
from services.log_parser.interfaces.api.router import router as log_router
from shared.logging_engine import configure_logging, LoggingMiddleware

configure_logging(env="prod", module_name="log_parser")

app = FastAPI(
    title="TestLens Log Parser API",
    description="Parses CI job logs into structured test events.",
    version="1.0.0"
)

app.add_middleware(LoggingMiddleware)
app.include_router(log_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
