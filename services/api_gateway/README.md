# API Gateway

The single public-facing FastAPI application that composes all sub-modules into a unified API surface.

## Responsibilities
1. **Routing**: Composes routers from `auth`, `users`, `failures`, `analytics`, and `notifications`.
2. **Unified OpenAPI**: Serves a single `/docs` page tagged by domain.
3. **CORS Enforcement**: Enforces explicit `ALLOWED_ORIGINS` loaded from `shared/config`. In `prod` environments, it explicitly crashes on startup if wildcard `*` origins are detected.
4. **Global Exception Mapping**: Intercepts every exception thrown by sub-modules and maps them to a consistent JSON error envelope `{"error": {"code": "...", "message": "...", "trace_id": "..."}}`.
5. **Security**: Never leaks raw `ValueError` or `KeyError` messages to the client. Unhandled 500s are masked to a generic support message, while the full traceback is logged server-side alongside the `X-Request-Id`.
6. **Rate Limiting**: Applies Tiered limits. Unauthenticated users get 100 req/min. Authenticated users (Bearer token present) get 1000 req/min.
7. **Traceability**: Injects an `X-Request-Id` into every request (using an upstream proxy's header if provided, otherwise generating a UUID), binds it to the shared logging engine context, and guarantees it is returned in the response headers.
8. **Probes**: Exposes `/healthz` (liveness) and `/readyz` (readiness) for Kubernetes orchestration. `/readyz` explicitly checks Postgres and Redis connectivity and returns 503 if downstream dependencies are offline, preventing black-holing traffic.
