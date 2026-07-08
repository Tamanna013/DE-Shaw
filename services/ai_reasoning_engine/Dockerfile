FROM python:3.12-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.12-slim
WORKDIR /app

# Pre-download the model at build time so the container boots fast
ENV SENTENCE_TRANSFORMERS_HOME=/app/.cache
RUN pip install sentence-transformers
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

RUN useradd -m testlens
USER testlens
COPY --from=builder /root/.local /home/testlens/.local
ENV PATH=/home/testlens/.local/bin:$PATH

COPY shared /app/shared
COPY services/ai_reasoning_engine /app/services/ai_reasoning_engine

CMD ["uvicorn", "services.ai_reasoning_engine.main:app", "--host", "0.0.0.0", "--port", "8005"]
