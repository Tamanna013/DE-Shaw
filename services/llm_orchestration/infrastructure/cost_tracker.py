from services.llm_orchestration.application.ports import CostTrackerPort
from services.llm_orchestration.domain.entities import CompletionResponse
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class InMemoryCostTracker(CostTrackerPort):
    """
    In a real application, this writes to PostgreSQL (Module 15 analytics tables).
    For this mock implementation, it logs costs and keeps an in-memory counter.
    """
    def __init__(self):
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0

    async def track_cost(self, response: CompletionResponse) -> None:
        self.total_prompt_tokens += response.usage.prompt_tokens
        self.total_completion_tokens += response.usage.completion_tokens
        
        # Simple hardcoded mock pricing model for demonstration
        prompt_cost = (response.usage.prompt_tokens / 1000) * 0.01
        comp_cost = (response.usage.completion_tokens / 1000) * 0.03
        total_cost = prompt_cost + comp_cost
        
        logger.debug("Cost tracked", 
                     provider=response.provider_name, 
                     model=response.model_name, 
                     cost_usd=round(total_cost, 5), 
                     total_system_prompt_tokens=self.total_prompt_tokens)
