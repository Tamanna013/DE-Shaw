# Contributing to TestLens

Welcome to the TestLens repository. This document outlines the standards required for submitting code.

## Required CI Checks for Merge
We enforce strict branch protection rules on `main`. Before any PR can be merged, the following status checks must pass:
1. **Service-Specific CI**: The workflow for the specific service you modified (e.g., `CI - Auth Service`) must pass. This includes:
   - Ruff linting and formatting.
   - Mypy strict type checking.
   - Pytest unit and integration tests.
   - **Coverage**: Test coverage on *changed files* must remain above 85% (enforced via `diff-cover`).
2. **Full-Stack Smoke Test**: The `CI - Full Stack Smoke Test` workflow runs on *every* PR. It boots the entire `docker-compose.yml` stack, waits for readiness, and executes an integration smoke test to ensure no cross-service breaking changes were introduced.
3. **Shared Packages**: If you modify `shared/**`, *all* service CI workflows will trigger and must pass, as they all depend on the shared kernel.

## Local Development & Validation

You can mirror the CI checks locally before pushing using the provided `Makefile`.

```bash
# Format and lint all Python code (fixes auto-fixable issues)
make lint

# Run type checking across all services
make typecheck

# Run unit tests for a specific service
make test SERVICE=auth

# Run the full-stack compose smoke test locally
make smoke-test
```

## Secret Management in CI
Never commit secrets. In GitHub Actions, secrets (like `ANTHROPIC_API_KEY`) are injected at runtime exclusively into the jobs that explicitly require them. When writing new workflows, ensure you are not passing global secrets to jobs that only run unit tests.
