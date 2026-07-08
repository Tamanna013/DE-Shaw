# TestLens Log Parser

Ingests arbitrary CI job logs and extracts structured events via a high-performance $O(N)$ Strategy-pattern regex engine.

## Supported Formats
- Pytest (Standard and `pytest-xdist` parallel logs)
- JUnit XML
- Jest
- Generic heuristic fallback

## Running locally

```bash
pip install -r requirements.txt
uvicorn services.log_parser.main:app --port 8002
```

## Performance Note
This service is designed to process 10MB log files in under 2 seconds. The log payloads should be chunked if they exceed 50MB, or sent via blob storage reference (URL).
