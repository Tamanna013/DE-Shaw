from celery import Celery
import os

# Uses the same broker as the Failure Analyzer (Module 7)
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

app = Celery(
    'testlens_analytics_batch',
    broker=redis_url,
    backend=redis_url,
    include=['services.analytics_batch.infrastructure.scheduled_tasks']
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    # Overlap protection is handled manually in the tasks via shared/caching locks
)
