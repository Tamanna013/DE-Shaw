FROM python:3.12-slim as builder
WORKDIR /app
# Mock requirements
RUN pip install --user fastapi uvicorn slowapi

FROM python:3.12-slim
WORKDIR /app

RUN useradd -m testlens
USER testlens
COPY --from=builder /root/.local /home/testlens/.local
ENV PATH=/home/testlens/.local/bin:$PATH

COPY shared /app/shared
COPY services/api_gateway /app/services/api_gateway

EXPOSE 8000

# Docker healthcheck uses our /healthz endpoint
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

CMD ["uvicorn", "services.api_gateway.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
