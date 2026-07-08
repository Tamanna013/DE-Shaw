# Infrastructure & Containerization

This directory centralizes the Docker definitions and local orchestration logic for the entire TestLens platform.

## Shared Base Images
To guarantee consistency and minimize supply-chain drift, all services must build upon one of our shared base images:
- `infra/docker/base-python.Dockerfile`
- `infra/docker/base-node.Dockerfile`

### Strict Pinned Digests
Notice that the base images use explicit SHA256 digests (e.g., `python:3.12-slim@sha256:4d602...`) rather than mutable tags like `:latest` or `:3.12-slim`. This ensures that every developer and CI runner is building atop the exact same byte-for-byte OS layer, preventing "it works on my machine" bugs caused by upstream apt package updates.

*Rotation Policy*: DevSecOps explicitly rotates these SHA digests on the 1st of every month via an automated dependabot/renovate PR, picking up security patches.

## Multi-stage & Non-Root Execution
Every service Dockerfile must enforce:
1. A multi-stage build (installing C-extensions in `builder`, discarding compilers in the final runtime image).
2. Execution as a non-root user (`USER appuser`). Running containers as `root` is strictly banned.

## Deterministic Boot Ordering
The root `docker-compose.yml` uses Docker Compose v2's `depends_on: <service>: condition: service_healthy` syntax.
This guarantees that `api_gateway` will absolutely not attempt to boot until Postgres and Redis have fully initialized their sockets. This eliminates the need for messy `wait-for-it.sh` sleep scripts in the entrypoints.

## Local Hot Reloading
For local development, copy `docker-compose.override.yml.example` to `docker-compose.override.yml`. Compose automatically merges these settings. This override maps your local source code into the containers via bind mounts and enables `uvicorn --reload` / `npm run dev`, allowing you to see changes instantly without rebuilding images.
