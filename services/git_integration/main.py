from fastapi import FastAPI
from services.git_integration.interfaces.api.router import router as git_router
from shared.logging_engine import configure_logging, LoggingMiddleware

configure_logging(env="prod", module_name="git_integration")

app = FastAPI(
    title="TestLens Git Integration API",
    description="Provider-agnostic git repository access and webhook handlers.",
    version="1.0.0"
)

app.add_middleware(LoggingMiddleware)
app.include_router(git_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
