# testlens-pytest

The official Pytest integration for TestLens.

This plugin seamlessly captures test outcomes, execution durations, captured stdout/stderr, and environment fingerprints, streaming them securely to your TestLens ingestion endpoint.

## Installation

```bash
pip install testlens-pytest
```

## Configuration

Set the following environment variables in your CI pipeline:

- `TESTLENS_API_KEY`: Your project's API key. **Required**. (If omitted, the plugin gracefully no-ops).
- `TESTLENS_REPO_ID`: The UUID of your repository. Default: `default_repo`.
- `TESTLENS_ENDPOINT`: Custom ingestion endpoint (default: `https://api.testlens.io/v1/ingest/pytest`).
- `TESTLENS_BATCH_SIZE`: How many tests to buffer before issuing an HTTP POST (default: 20).
- `TESTLENS_MAX_OUTPUT_SIZE`: Maximum bytes of stdout/stderr to capture per test before truncating (default: 100000).

## Design Philosophy

This plugin is designed to be **Zero-Risk** to your CI pipeline.
- It will NEVER fail your test run due to a TestLens API outage or network timeout.
- It defaults to dropping payloads with a local console warning if it cannot reach the server after 1 retry.
- It operates using synchronous, buffered HTTP batches to maintain a minimal footprint on your test suite execution time (< 2% overhead).
