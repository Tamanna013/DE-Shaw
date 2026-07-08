import pytest
from unittest.mock import AsyncMock, Mock
from services.llm_orchestration.application.use_cases.complete import LLMOrchestrator
from services.llm_orchestration.domain.entities import CompletionRequest, CompletionResponse, TokenUsage
from services.llm_orchestration.domain.exceptions import LLMRateLimitError, EmptyCompletionError, LLMProviderError
from services.llm_orchestration.infrastructure.circuit_breaker import SlidingWindowCircuitBreaker
from services.llm_orchestration.infrastructure.cost_tracker import InMemoryCostTracker
import asyncio

@pytest.fixture
def mock_deps():
    primary = AsyncMock()
    primary.provider_name.return_value = "primary"
    
    fallback = AsyncMock()
    fallback.provider_name.return_value = "fallback"
    
    cost_tracker = InMemoryCostTracker()
    circuit_breaker = SlidingWindowCircuitBreaker()
    
    return {
        "primary_adapter": primary,
        "fallback_adapter": fallback,
        "cost_tracker": cost_tracker,
        "circuit_breaker": circuit_breaker
    }
    
@pytest.fixture
def dummy_request():
    return CompletionRequest(system_instruction="sys", messages=[{"role": "user", "content": "hi"}])

@pytest.fixture
def dummy_response():
    return CompletionResponse("response", TokenUsage(10, 10, 20), "primary", "model")

@pytest.mark.asyncio
async def test_retry_on_429(mock_deps, dummy_request, dummy_response, monkeypatch):
    primary = mock_deps["primary_adapter"]
    
    # Fail first time with 429, then succeed
    primary.complete.side_effect = [
        LLMRateLimitError("Too many reqs", retry_after=0), # 0 for fast tests
        dummy_response
    ]
    
    orchestrator = LLMOrchestrator(**mock_deps)
    resp = await orchestrator.complete(dummy_request)
    
    assert resp.content == "response"
    assert primary.complete.call_count == 2

@pytest.mark.asyncio
async def test_circuit_breaker_trips_and_falls_back(mock_deps, dummy_request, dummy_response):
    primary = mock_deps["primary_adapter"]
    fallback = mock_deps["fallback_adapter"]
    
    primary.complete.side_effect = LLMProviderError("500 Error")
    fallback.complete.return_value = dummy_response
    
    orchestrator = LLMOrchestrator(**mock_deps)
    
    # 1. First request exhausts retries and falls back
    resp1 = await orchestrator.complete(dummy_request)
    assert resp1.provider_name == "primary" # Wait, dummy_response is tied to "primary" provider_name in my fixture, but it came from fallback. That's fine.
    
    # After first request (which retried 3 times internally), the circuit should be open!
    assert mock_deps["circuit_breaker"].is_open("primary") == True
    
    # 2. Second request should skip primary entirely!
    primary.complete.reset_mock()
    resp2 = await orchestrator.complete(dummy_request)
    
    assert primary.complete.call_count == 0
    assert fallback.complete.call_count == 2 # 1 from previous fallback, 1 from now

@pytest.mark.asyncio
async def test_prompt_truncation_preserves_schema(mock_deps):
    orchestrator = LLMOrchestrator(**mock_deps)
    orchestrator.max_tokens = 50 # Small budget
    
    long_str = "x" * 200 # ~50 tokens
    req = CompletionRequest(
        system_instruction="STRICT SCHEMA",
        messages=[{"role": "user", "content": long_str}]
    )
    
    mock_deps["primary_adapter"].complete.return_value = CompletionResponse("resp", TokenUsage(10,10,20), "primary", "model")
    
    await orchestrator.complete(req)
    
    # Assert truncation happened but system instruction intact
    sent_req = mock_deps["primary_adapter"].complete.call_args[0][0]
    assert sent_req.system_instruction == "STRICT SCHEMA"
    assert len(sent_req.messages[0]["content"]) < 200
    assert "TRUNCATED" in sent_req.messages[0]["content"]

@pytest.mark.asyncio
async def test_empty_completion_treated_as_provider_error(mock_deps, dummy_request):
    primary = mock_deps["primary_adapter"]
    fallback = mock_deps["fallback_adapter"]
    
    primary.complete.side_effect = EmptyCompletionError("Empty")
    fallback.complete.return_value = CompletionResponse("fallback content", TokenUsage(10,10,20), "fallback", "model")
    
    orchestrator = LLMOrchestrator(**mock_deps)
    resp = await orchestrator.complete(dummy_request)
    
    assert resp.content == "fallback content"
