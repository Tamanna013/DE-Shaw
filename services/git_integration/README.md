# TestLens Git Integration

Provides authenticated, rate-limit-aware access to source repositories (GitHub, GitLab) for fetching commit metadata and diffs.

## Dual-Fetch Architecture
Because analyzing massive repositories can quickly exhaust GitHub/GitLab API rate limits (especially when pulling diffs for every single commit), this module implements a **Local Mirror Fallback**:
1. It queries the API provider for remaining rate limit quota.
2. If quota is ample, it hits the API directly (stateless, fast).
3. If quota drops below the threshold (or if the API 404s/500s), it seamlessly fails over to the `ShallowCloneManager`.
4. The clone manager issues a bare Git clone to a local persistent volume (`/tmp/testlens_git_cache`) and uses local `git` CLI subprocesses to extract metadata and diffs without incurring API cost.

## Webhooks
Includes a highly-optimized webhook ingestion endpoint `POST /api/v1/repos/{id}/webhook`:
- Strictly enforces `X-Hub-Signature-256` HMAC validation against stored secrets.
- Performs zero synchronous processing. Successfully authenticated events are immediately dropped onto the task queue for background processing (sub-100ms response time).
