from fastapi import APIRouter, HTTPException
from services.llm_orchestration.interfaces.api.schemas import CompletionRequestSchema, CompletionResponseSchema, TokenUsageSchema
from services.llm_orchestration.domain.entities import CompletionRequest
from services.llm_orchestration.application.use_cases.complete import LLMOrchestrator
from services.llm_orchestration.infrastructure.providers.anthropic_adapter import AnthropicAdapter
from services.llm_orchestration.infrastructure.providers.openai_adapter import OpenAIAdapter
from services.llm_orchestration.infrastructure.cost_tracker import InMemoryCostTracker
from services.llm_orchestration.infrastructure.circuit_breaker import SlidingWindowCircuitBreaker
from shared.logging_engine import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/llm", tags=["llm_orchestration"])

# Dependency setup (Singleton-ish for circuit breaker state)
circuit_breaker = SlidingWindowCircuitBreaker(failure_threshold=3, cooldown_seconds=60)
cost_tracker = InMemoryCostTracker()
anthropic = AnthropicAdapter()
openai = OpenAIAdapter()

orchestrator = LLMOrchestrator(
    primary_adapter=anthropic,
    fallback_adapter=openai,
    cost_tracker=cost_tracker,
    circuit_breaker=circuit_breaker
)

@router.post("/complete", response_model=CompletionResponseSchema)
async def complete(req: CompletionRequestSchema):
    domain_req = CompletionRequest(
        system_instruction=req.system_instruction,
        messages=req.messages,
        max_tokens=req.max_tokens,
        temperature=req.temperature
    )
    
    try:
        resp = await orchestrator.complete(domain_req)
        return CompletionResponseSchema(
            content=resp.content,
            usage=TokenUsageSchema(
                prompt_tokens=resp.usage.prompt_tokens,
                completion_tokens=resp.usage.completion_tokens,
                total_tokens=resp.usage.total_tokens
            ),
            provider_name=resp.provider_name,
            model_name=resp.model_name
        )
    except Exception as e:
        logger.error("Orchestrator complete failed completely", exc_info=e)
        raise HTTPException(status_code=502, detail="LLM providers are unavailable")
