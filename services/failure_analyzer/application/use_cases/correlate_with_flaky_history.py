from typing import List, Optional
from services.failure_analyzer.application.ports import FailureHistoryRepositoryPort
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class CorrelateWithFlakyHistoryUseCase:
    def __init__(self, history_repo: FailureHistoryRepositoryPort):
        self.history_repo = history_repo

    async def execute(self, test_case_id: str, threshold: float = 0.15) -> dict:
        try:
            history = await self.history_repo.get_test_case_history(test_case_id, days=90)
            
            passes = history.get('passes', 0)
            fails = history.get('fails', 0)
            total = passes + fails
            
            if total < 5:
                return {"is_flaky": False, "flip_rate": 0.0, "reason": "insufficient_data"}
                
            flip_rate = fails / total
            
            is_flaky = flip_rate > threshold
            if is_flaky:
                logger.info("High flaky signal detected", test_case_id=test_case_id, flip_rate=flip_rate)
                
            return {
                "is_flaky": is_flaky,
                "flip_rate": flip_rate,
                "passes": passes,
                "fails": fails
            }
        except Exception as e:
            logger.error("Failed to compute flaky history", exc_info=e)
            return {"is_flaky": False, "flip_rate": 0.0, "error": str(e)}
