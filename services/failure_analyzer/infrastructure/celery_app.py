import os
from celery import Celery

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# Pick Celery over RQ because we need exponential backoff retries, complex routing
# if we scale out AI vs fast parsers, and robust monitoring (Flower) out of the box.
celery_app = Celery(
    "failure_analyzer",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300, # 5 min max
)
