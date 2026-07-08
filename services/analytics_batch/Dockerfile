FROM python:3.12-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.12-slim
WORKDIR /app

RUN useradd -m testlens
USER testlens
COPY --from=builder /root/.local /home/testlens/.local
ENV PATH=/home/testlens/.local/bin:$PATH

COPY shared /app/shared
COPY services/analytics_batch /app/services/analytics_batch

# Default to running Celery beat, but can be overridden in compose to run workers
CMD ["celery", "-A", "services.analytics_batch.infrastructure.celery_app", "beat", "--loglevel=info"]
