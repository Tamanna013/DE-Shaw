# TestLens Stack Trace Parser

Parses stack traces from multiple languages (Python, Java, JS, Go), normalizes them by stripping dynamic tokens (memory addresses, timestamps), and extracts structured frames.

## Features
- **Normalization Engine**: Generates a `normalized_signature` to hash identical failures together, stripping out environment-specific noise.
- **Language Detection**: Automatically routes trace to the correct language parser.
- **Source Context**: Integrates with `git_integration` (Module 11) to pull down the actual lines of code that threw the exception.

## Running locally

```bash
pip install -r requirements.txt
uvicorn services.stack_trace_parser.main:app --port 8003
```
