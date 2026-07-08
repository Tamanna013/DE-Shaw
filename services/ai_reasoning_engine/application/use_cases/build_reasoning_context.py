from typing import List, Dict, Any
from services.ai_reasoning_engine.domain.entities import ReasoningContext, HistoricalFailureInfo
from services.ai_reasoning_engine.domain.exceptions import MissingContextError
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class BuildReasoningContextUseCase:
    def execute(self, 
                execution_id: str, 
                test_case_id: str, 
                context_bundle: Dict[str, Any], 
                historical_failures: List[HistoricalFailureInfo]) -> ReasoningContext:
        
        log_excerpt = context_bundle.get("log_excerpt")
        stack_trace = context_bundle.get("stack_trace")
        
        if not log_excerpt and not stack_trace:
            logger.error("Context bundle missing both log and stack trace", execution_id=execution_id)
            raise MissingContextError("Rejecting context bundle missing both stack trace and log excerpt")
            
        ctx = ReasoningContext(
            execution_id=execution_id,
            test_case_id=test_case_id,
            log_excerpt=log_excerpt,
            stack_trace=stack_trace,
            flaky_signal=context_bundle.get("flaky_signal"),
            commits=context_bundle.get("commits", []),
            similar_historical_failures=historical_failures
        )
        return ctx
