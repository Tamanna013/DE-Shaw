FROM python:3.12-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.12-slim as runtime
WORKDIR /app
RUN useradd -m testlens
USER testlens
COPY --from=builder /root/.local /home/testlens/.local
ENV PATH=/home/testlens/.local/bin:$PATH
COPY shared /app/shared
COPY services/failure_analyzer /app/services/failure_analyzer

FROM runtime as api
CMD ["uvicorn", "services.failure_analyzer.main:app", "--host", "0.0.0.0", "--port", "8004"]

FROM runtime as worker
CMD ["celery", "-A", "services.failure_analyzer.infrastructure.celery_app", "worker", "--loglevel=info"]
