# TestLens Failure Analyzer

The central orchestration module that triggers the failure analysis pipeline.

## Pipeline Architecture
1. Validates execution status and acquires a Redis lock to prevent duplicate concurrent analyses.
2. Calls `LogParserPort` and `StackTraceParserPort` to normalize error signals.
3. Computes flaky test history via the `FailureHistoryRepository`.
4. Retrieves and ranks recent commits via the `CommitAnalyzerPort` (overlap scoring).
5. Bundles context and delegates to the `AIReasoningPort`.
6. Merges deterministic signals (flaky, code-change absence) with AI hypotheses.
7. Persists `FailureAnalysisReport` and drops an outbox event `failure.analyzed`.

## Stack
- **FastAPI**: Ingestion API.
- **Celery + Redis**: Background orchestration. Chosen over RQ for built-in exponential backoff retries, ETA scheduling, and robust monitoring tooling (Flower) for long-running LLM tasks.
