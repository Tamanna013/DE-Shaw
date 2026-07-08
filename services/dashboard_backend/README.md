# TestLens Dashboard Backend

Serves aggregated, query-optimized metrics and trends to the frontend dashboard. 

## Architectural Choices
While the rest of the application uses SQLAlchemy ORM, the `dashboard_backend` is explicitly designed around **SQLAlchemy Core** `text()` queries for performance-critical endpoints like `/trends/failures` and `/leaderboard/flaky-tests`.

Aggregating massive tables (like `test_case_executions` spanning millions of rows) via ORM mapping is prohibitively slow and memory intensive. By writing hand-tuned SQL using `DATE_TRUNC`, we push the aggregation to PostgreSQL directly.

## Performance & Caching
1. **Query Bounding**: All trend queries strictly enforce a 1-year date range cap to prevent users from accidentally issuing unbounded sequence scans.
2. **Caching**: Every endpoint is wrapped in the shared `@cached` decorator, leveraging Redis with TTLs ranging from 5 to 10 minutes. This means that 100 users opening the dashboard simultaneously results in only **1** hit to the Postgres database, completely eliminating read-load issues.
3. **Indexes Verified**: The raw SQL relies heavily on composite indexes:
   - `test_case_executions (repository_id, created_at)`
   - `flaky_test_signals (repository_id, flaky_score DESC)`
