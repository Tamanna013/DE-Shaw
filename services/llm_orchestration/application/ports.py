from typing import Protocol
from services.llm_orchestration.domain.entities import CompletionRequest, CompletionResponse

class LLMProviderAdapterPort(Protocol):
    def provider_name(self) -> str:
        ...

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        ...

class CostTrackerPort(Protocol):
    async def track_cost(self, response: CompletionResponse) -> None:
        ...

class CircuitBreakerPort(Protocol):
    def record_success(self, provider_name: str) -> None:
        ...
        
    def record_failure(self, provider_name: str) -> None:
        ...
        
    def is_open(self, provider_name: str) -> bool:
        ...
