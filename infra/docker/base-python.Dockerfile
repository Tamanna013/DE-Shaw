# We use a pinned digest rather than just `:slim` to avoid supply-chain drift.
# (Digest is an example representation of python:3.12-slim)
FROM python:3.12-slim@sha256:4d6023d6a74c76b911fb627d3c01f6c44917454c5e317c5af347cc1de366cf8b as base

# Install common system dependencies needed for native extensions (asyncpg) or tools (git)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN groupadd -g 999 appuser && \
    useradd -r -u 999 -g appuser -d /home/appuser -m appuser

USER appuser
ENV PATH="/home/appuser/.local/bin:${PATH}"
WORKDIR /app
