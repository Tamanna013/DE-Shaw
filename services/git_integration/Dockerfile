FROM python:3.12-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.12-slim
WORKDIR /app

# Install git for the shallow clone manager
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

RUN useradd -m testlens
USER testlens
COPY --from=builder /root/.local /home/testlens/.local
ENV PATH=/home/testlens/.local/bin:$PATH

COPY shared /app/shared
COPY services/git_integration /app/services/git_integration

# Local mirror storage volume
VOLUME /tmp/testlens_git_cache

CMD ["uvicorn", "services.git_integration.main:app", "--host", "0.0.0.0", "--port", "8007"]
