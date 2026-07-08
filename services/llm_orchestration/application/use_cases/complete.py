import asyncio
from tenacity import retry, retry_if_exception_type, wait_exponential, stop_after_attempt, wait_fixed
from typing import Dict, Any, Optional
from services.llm_orchestration.domain.entities import CompletionRequest, CompletionResponse
from services.llm_orchestration.domain.exceptions import LLMRateLimitError, LLMProviderError, LLMTimeoutError, EmptyCompletionError
from services.llm_orchestration.application.ports import LLMProviderAdapterPort, CostTrackerPort, CircuitBreakerPort
from shared.logging_engine import get_logger
import time
import os

logger = get_logger(__name__)

# To dynamically wait based on retry-after header if present, tenacity provides a way via wait_func.
# But for simplicity, we'll use exponential backoff, and explicitly sleep in the loop if rate limited.

class LLMOrchestrator:
    def __init__(self, 
                 primary_adapter: LLMProviderAdapterPort, 
                 fallback_adapter: LLMProviderAdapterPort,
                 cost_tracker: CostTrackerPort,
                 circuit_breaker: CircuitBreakerPort):
        self.primary_adapter = primary_adapter
        self.fallback_adapter = fallback_adapter
        self.cost_tracker = cost_tracker
        self.circuit_breaker = circuit_breaker
        self.log_payloads = os.environ.get("LOG_LLM_PAYLOADS", "false").lower() == "true"
        self.max_tokens = int(os.environ.get("LLM_MAX_PROMPT_TOKENS", "8000"))

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        # 1. Truncate context intelligently if needed
        self._truncate_request_if_needed(request)
        
        provider = self.primary_adapter
        if self.circuit_breaker.is_open(provider.provider_name()):
            logger.warning("Primary provider circuit open, falling back", primary=provider.provider_name(), fallback=self.fallback_adapter.provider_name())
            provider = self.fallback_adapter
            
        try:
            response = await self._call_with_retries(provider, request)
        except Exception as e:
            # If primary completely fails after retries, try fallback once (if we didn't already start with fallback)
            if provider == self.primary_adapter:
                logger.warning("Primary provider failed completely. Falling back.", exc_info=e)
                provider = self.fallback_adapter
                response = await self._call_with_retries(provider, request)
            else:
                raise
                
        # Cost tracking
        await self.cost_tracker.track_cost(response)
        
        return response

    async def _call_with_retries(self, provider: LLMProviderAdapterPort, request: CompletionRequest) -> CompletionResponse:
        attempts = 0
        max_attempts = 3
        while attempts < max_attempts:
            attempts += 1
            try:
                start_time = time.perf_counter()
                
                if self.log_payloads:
                    logger.debug("LLM Request", request=request.__dict__)
                    
                response = await provider.complete(request)
                
                latency_ms = (time.perf_counter() - start_time) * 1000
                logger.info("LLM Call Success", 
                            provider=provider.provider_name(), 
                            model=response.model_name, 
                            latency_ms=round(latency_ms, 2),
                            prompt_tokens=response.usage.prompt_tokens,
                            completion_tokens=response.usage.completion_tokens)
                            
                self.circuit_breaker.record_success(provider.provider_name())
                return response
                
            except LLMRateLimitError as rle:
                logger.warning("LLM Rate Limit", provider=provider.provider_name(), retry_after=rle.retry_after)
                self.circuit_breaker.record_failure(provider.provider_name())
                if attempts == max_attempts:
                    raise
                await asyncio.sleep(rle.retry_after)
                
            except (LLMTimeoutError, EmptyCompletionError) as e:
                logger.warning("LLM Transient Error", provider=provider.provider_name(), error=str(e))
                self.circuit_breaker.record_failure(provider.provider_name())
                if attempts == max_attempts:
                    raise
                await asyncio.sleep(2 ** attempts) # Exponential backoff
                
            except LLMProviderError as e:
                # E.g. a 400 Bad Request content error. Do not retry these.
                logger.error("LLM Provider Content Error", provider=provider.provider_name(), error=str(e))
                # Do not record failure on the circuit breaker for 4xx errors usually, but for 5xx we do.
                # Assuming LLMProviderError maps strictly to 4xx if not caught as something else.
                raise

    def _truncate_request_if_needed(self, request: CompletionRequest):
        # A very simplified heuristic truncation strategy.
        # It approximates tokens (4 chars ~= 1 token).
        # We guarantee we never truncate the system instruction (where JSON schema lives).
        # We start truncating the earliest user messages first if needed.
        system_len = len(request.system_instruction or "") // 4
        
        while sum((len(m.get("content", "")) // 4) for m in request.messages) + system_len > self.max_tokens:
            if not request.messages:
                break
            
            # Find the first user/context message and truncate it
            for i, msg in enumerate(request.messages):
                if msg.get("role") != "system": # Ensure we aren't truncating instructions
                    content_len = len(msg.get("content", ""))
                    if content_len > 1000:
                        # Slice aggressively
                        request.messages[i]["content"] = msg["content"][:content_len//2] + "\n...[TRUNCATED_BY_ORCHESTRATOR]..."
                    else:
                        # Drop message entirely if too small
                        request.messages.pop(i)
                    break
