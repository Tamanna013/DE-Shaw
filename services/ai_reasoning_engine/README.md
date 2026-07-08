# TestLens AI Reasoning Engine

This module forms the cognitive core of TestLens. It implements a robust Retrieval-Augmented Generation (RAG) pipeline for test failure analysis.

## Pipeline Architecture
1. **Embedding**: Uses `all-MiniLM-L6-v2` (~90MB memory footprint, <50ms CPU inference) to vectorise stack trace signatures.
2. **Retrieval**: Uses PostgreSQL `pgvector` to find semantically identical past failures across millions of test runs using IVFFLAT indexes.
3. **Reasoning**: Delegates the contextualized prompt to the LLM Orchestrator (Module 9/10).
4. **Validation & Repair**: Validates LLM responses via Pydantic schemas. If the LLM hallucinates ungrounded evidence or malformed JSON, it attempts a targeted repair prompt.
5. **Hallucination Mitigation**: Uses a composite confidence score:
   - 40% LLM Self-Reported Confidence (Bounded)
   - 35% Retrieval Grounding Evidence (Did it cite actual pgvector results?)
   - 25% Deterministic Agreement (Did the logic match git commit correlations or flaky flip-rates?)
   
If the score falls below `0.3`, it degrades gracefully to a rule-based deterministic fallback rather than surfacing garbage to the developer.

## Running Locally

```bash
docker-compose up
```
*(Note: Initial boot pulls the 90MB sentence-transformer model).*
