# TestLens

TestLens is an AI-powered CI failure analysis platform designed to automatically ingest, parse, analyze, and resolve test failures across large engineering organizations. Built with Clean Architecture principles, it features robust integrations, deterministic machine learning scoring, and a suite of microservices designed for enterprise-scale reliability.

## 🚀 Features Implemented

The platform consists of a highly decoupled set of microservices:

1. **Authentication & User Management**: JWT-based auth, Role-Based Access Control (RBAC), and GitHub/GitLab OAuth.
2. **Log Parser**: Ingests raw CI job logs and extracts structured events via an $O(N)$ single-pass architecture.
3. **Stack Trace Parser**: Normalizes captured stderr/stdout blocks into structured domain objects.
4. **Git Integration**: Provides authenticated, rate-limit-aware access to source repositories for fetching commit metadata and diffs.
5. **Commit Analyzer**: Computes deterministic commit-to-test correlation signals to identify exactly which commit broke a test.
6. **AI Reasoning Engine**: A Retrieval-Augmented Generation (RAG) module providing cognitive reasoning against historical failures.
7. **LLM Orchestration**: The sole module authorized to make outbound HTTP requests to LLM providers (Anthropic, OpenAI), managing token budgets and retries.
8. **Prompt Templates**: A versioned, testable registry of LLM prompt templates (Jinja2).
9. **Failure Analyzer Orchestrator**: The central hub that orchestrates the entire failure analysis pipeline, tying together logs, git context, and AI reasoning.
10. **Analytics Batch Processing**: Scheduled Celery beat jobs that compute expensive aggregate signals off the critical path, including Flaky Test Scoring using the Wilson Score Interval.
11. **Dashboard Backend**: Serves aggregated, query-optimized metrics and trends via `sqlalchemy.text()` aggregations.
12. **Notifications System**: Consumes domain events via the transactional outbox pattern and routes them to user-configured channels (In-App, Email, Slack).
13. **API Gateway**: A single public-facing FastAPI application that composes all sub-modules, handles rate-limiting, CORS, and provides a unified OpenAPI specification.
14. **React Frontend**: The primary UI surface built with React, Vite, TailwindCSS, and TanStack Query.
15. **UI Component Library (`@testlens/ui`)**: A strict, CVA-driven design system enforcing visual consistency and WCAG compliance.
16. **TestLens CLI**: A blazing-fast, scriptable terminal interface for SDETs.
17. **Pytest Plugin (`testlens-pytest`)**: A first-party integration that streams execution metadata directly to the platform.

## 🛠️ Technology Stack

- **Backend / Microservices**: Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Celery, Typer (CLI)
- **Frontend**: React 18, TypeScript, TailwindCSS, Vite, TanStack Query, class-variance-authority (CVA), Storybook, Playwright
- **Databases & Caching**: PostgreSQL 15 (with `pgvector`), Redis 7 (Caching, Distributed Locks, Celery Broker)
- **Infrastructure & Orchestration**: Docker, Docker Compose, GitHub Actions (CI/CD)

## 🏗️ Architecture Guarantees

- **Clean Architecture**: Every module strictly follows `domain/ -> application/ -> infrastructure/ -> interfaces/`.
- **Secret Safety**: All configuration flows through a heavily validated Pydantic layer (`shared/config`) utilizing `SecretStr` to prevent token leakage in logs.
- **Fail-Fast Startup**: Microservices crash instantly on boot if a required environment variable is missing, avoiding runtime surprises.
- **Deterministic Boot**: Docker orchestration uses `service_healthy` conditions. The APIs literally cannot boot until Postgres and Redis are fully online.
- **Global Error Envelopes**: The API Gateway intercepts all domain exceptions and maps them to standard JSON errors, completely masking internal stack traces from clients.

---

## 🏃 How to Run the Complete App Locally

We use Docker Compose to orchestrate the entire platform locally.

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine installed.
- Docker Compose v2.

### Step 1: Environment Variables
All microservices come with a `.env.example` file in their respective directories.
For local development, the default values injected by Docker Compose will work out of the box. 

### Step 2: Enable Hot Reloading (Optional)
To enable hot-reloading for local development (so that changes to Python files automatically restart Uvicorn, and changes to React files instantly update the browser):
```bash
cp infra/docker/docker-compose.override.yml.example infra/docker/docker-compose.override.yml
```
*Docker Compose automatically reads `.override.yml` files and merges them.*

### Step 3: Boot the Stack
Navigate to the root directory of the repository and run:
```bash
docker-compose -f infra/docker/docker-compose.yml up --build -d
```
*(This first run will take a few minutes to download the PostgreSQL, Redis, Python, and Node base images and compile the dependencies).*

### Step 4: Verify Health
You can check the logs to see the services starting up:
```bash
docker-compose -f infra/docker/docker-compose.yml logs -f
```

Wait until the `api_gateway` reports that it is running. You can verify the health of the entire cluster by hitting the gateway's readiness probe:
```bash
curl http://localhost:8000/readyz
```
*You should receive a `{"status": "ok", "dependencies": {"db": "ok", "redis": "ok"}}` response.*

### Step 5: Access the Applications

Once booted, the following services are available:

- **Frontend Dashboard**: [http://localhost:5173](http://localhost:5173) (or `http://localhost:80` if not using the override)
- **Unified API Gateway (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **PostgreSQL Database**: `localhost:5432` (User: `postgres`, Password: `postgres`)
- **Redis Cache/Broker**: `localhost:6379`

### Tearing Down
To stop the application and remove the containers:
```bash
docker-compose -f infra/docker/docker-compose.yml down
```
*(Append `-v` if you also want to wipe the local database and redis volumes).*

## 🧪 Running Tests Locally

You can use the provided `Makefile` to run the CI checks on your host machine.

```bash
# Format and lint all code
make lint

# Type check all services
make typecheck

# Run unit tests for a specific service
make test SERVICE=auth

# Run the full-stack compose smoke test
make smoke-test
```
