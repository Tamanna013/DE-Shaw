# TestLens Prompt Templates

A versioned, testable registry of LLM prompt templates, consumed as an in-process library.

## Why an in-process library?
Since prompts need to be compiled against Pydantic models for validation, embedding them as a Python library directly into the `ai_reasoning_engine` (or any other consumer) minimizes HTTP overhead and strongly types the contracts. 

In a massive enterprise deployment where templates change daily and require zero-downtime hot-swapping without container restarts, this could be refactored into a sidecar or distinct gRPC service. But for V1, an importable package reading from disk (`infrastructure/templates`) is the simplest, most reliable mechanism.

## Features
1. **Co-located Schemas**: Every `.jinja2` file has a matching `.schema.py` file containing a Pydantic `BaseModel`. This ensures callers cannot pass invalid or incomplete variables to a template.
2. **Hallucination Mitigation**: All templates encode strict JSON schema outputs and explicit instructions to refuse answering if evidence is lacking.
3. **Dynamic Loading**: `FileBasedPromptTemplateRepository` dynamically loads the Pydantic classes at runtime, enabling hot-reloading in dev.

## Tests
Run `pytest` to ensure all templates render cleanly using their schema's `generate_example()` method.
