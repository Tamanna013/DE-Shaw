import math
from typing import List, Tuple
from datetime import datetime
from shared.logging_engine import get_logger
from services.analytics_batch.domain.entities import FlakyScoreResult
from services.analytics_batch.application.ports import BatchRepositoryPort, NotificationPort

logger = get_logger(__name__)

# --- Pure functions for scoring logic ---

def calculate_flip_rate(outcomes: List[str]) -> Tuple[float, int]:
    if len(outcomes) <= 1:
        return 0.0, 0
        
    flip_count = 0
    for i in range(1, len(outcomes)):
        if outcomes[i] != outcomes[i-1]:
            flip_count += 1
            
    return flip_count / (len(outcomes) - 1), flip_count

def calculate_wilson_score_lower_bound(flip_rate: float, n: int, z: float = 1.96) -> float:
    """
    Adjusts the raw flip rate downward if the sample size (n) is small,
    ensuring we don't confidently label a test "flaky" just because it flipped
    1 time out of 2 total executions (50% raw rate).
    z = 1.96 corresponds to a 95% confidence interval.
    """
    if n == 0:
        return 0.0
        
    # Standard Wilson score interval lower bound
    denominator = 1 + z**2 / n
    centre = flip_rate + z**2 / (2 * n)
    spread = z * math.sqrt((flip_rate * (1 - flip_rate) + z**2 / (4 * n)) / n)
    
    return max(0.0, (centre - spread) / denominator)

# --- Use Case ---

class ComputeFlakyScoresUseCase:
    # Threshold above which a test is actively flagged to the owning team
    FLAKY_THRESHOLD = 0.35 

    def __init__(self, repo: BatchRepositoryPort, notification_port: NotificationPort):
        self.repo = repo
        self.notification_port = notification_port

    async def execute(self, since_watermark: datetime) -> int:
        test_case_ids = await self.repo.get_test_cases_with_new_executions(since_watermark)
        processed_count = 0
        
        for tc_id in test_case_ids:
            try:
                repo_id = await self.repo.get_repository_id_for_test(tc_id)
                if not repo_id:
                    logger.warning(f"Test case {tc_id} orphaned or deleted. Skipping.")
                    continue
                    
                outcomes = await self.repo.get_execution_outcomes_ordered(tc_id, days_back=30)
                n = len(outcomes)
                
                flip_rate, flip_count = calculate_flip_rate(outcomes)
                
                # Confidence adjusted score
                # The sample size for flips is n-1 (number of transitions)
                sample_size = max(0, n - 1)
                adjusted_score = calculate_wilson_score_lower_bound(flip_rate, sample_size)
                
                result = FlakyScoreResult(
                    test_case_id=tc_id,
                    repository_id=repo_id,
                    flip_rate=flip_rate,
                    confidence_adjusted_score=adjusted_score,
                    flip_count=flip_count,
                    total_executions=n
                )
                
                await self.repo.upsert_flaky_score(result)
                
                if adjusted_score >= self.FLAKY_THRESHOLD:
                    await self.notification_port.emit_flaky_flagged_event(tc_id, adjusted_score)
                    
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Unhandled error scoring test {tc_id}", exc_info=e)
                # Continue batch despite individual item failure
                
        logger.info(f"compute_flaky_scores completed. Processed {processed_count} tests.")
        return processed_count
