# TestLens LLM Orchestrator

The sole module in the TestLens ecosystem authorized to make outbound HTTP requests to LLM providers.

## Core Features
1. **Provider-Agnostic Interface**: Supports multiple providers via the `LLMProviderAdapterPort`. Currently implements Anthropic (Primary) and OpenAI (Fallback).
2. **Circuit Breaker**: Tracks consecutive 429 and 5xx errors per provider. Automatically opens the circuit and diverts traffic to the fallback provider to ensure high availability.
3. **Resilience**: Implements exponential backoff with jitter on rate limits (respecting `Retry-After` headers if present) and transient network timeouts.
4. **Intelligent Truncation**: Enforces a strict context window budget (configurable, default 8000 tokens) by gracefully truncating low-priority user context while *always* preserving the system instruction (which contains the critical JSON schema definition).
5. **Cost Tracking**: All requests are intercepted by `CostTrackerPort` to maintain visibility over API spend per test case.

## Running Locally

```bash
export ANTHROPIC_API_KEY="..."
export OPENAI_API_KEY="..."
docker-compose up
```
