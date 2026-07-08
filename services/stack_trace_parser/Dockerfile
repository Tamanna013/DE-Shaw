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
COPY services/stack_trace_parser /app/services/stack_trace_parser

CMD ["uvicorn", "services.stack_trace_parser.main:app", "--host", "0.0.0.0", "--port", "8003"]
