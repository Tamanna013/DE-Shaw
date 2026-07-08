from fastapi import FastAPI
from services.notifications.interfaces.api.router import router as notifications_router
from shared.logging_engine import configure_logging, LoggingMiddleware

configure_logging(env="prod", module_name="notifications")

app = FastAPI(
    title="TestLens Notifications API",
    description="Manages in-app notifications and routing outbox events to external channels.",
    version="1.0.0"
)

app.add_middleware(LoggingMiddleware)
app.include_router(notifications_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
