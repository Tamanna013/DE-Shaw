from fastapi import FastAPI
from services.commit_analyzer.interfaces.api.router import router as commit_router
from shared.logging_engine import configure_logging, LoggingMiddleware

configure_logging(env="prod", module_name="commit_analyzer")

app = FastAPI(
    title="TestLens Commit Analyzer API",
    description="Scores candidate commits against stack traces to find regression culprits.",
    version="1.0.0"
)

app.add_middleware(LoggingMiddleware)
app.include_router(commit_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
