import pytest
import math
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

from services.analytics_batch.application.use_cases.compute_flaky_scores import ComputeFlakyScoresUseCase
from services.analytics_batch.domain.entities import FlakyScoreResult

class FakeBatchRepository:
    def __init__(self, seeded_outcomes):
        self.seeded_outcomes = seeded_outcomes
        self.upserted = []

    async def get_test_cases_with_new_executions(self, since: datetime):
        return list(self.seeded_outcomes.keys())

    async def get_execution_outcomes_ordered(self, test_case_id: str, days_back: int = 30):
        return self.seeded_outcomes.get(test_case_id, [])

    async def get_repository_id_for_test(self, test_case_id: str):
        return "repo-int"

    async def upsert_flaky_score(self, result: FlakyScoreResult):
        self.upserted.append(result)

@pytest.mark.asyncio
async def test_compute_flaky_scores_integration():
    # Scenario 1: Always passing (not flaky)
    # Scenario 2: Always failing (not flaky, just broken)
    # Scenario 3: Alternating perfectly (extremely flaky)
    # Scenario 4: 1 flip in 50 runs (low confidence, heavily discounted)
    
    seeded = {
        "tc-pass": ["passed"] * 50,
        "tc-fail": ["failed"] * 50,
        "tc-alt": ["passed", "failed"] * 25, # 50 runs, 49 flips. 100% flip rate.
        "tc-rare": ["passed"] * 48 + ["failed", "passed"] # 50 runs, 2 flips. 4% flip rate.
    }
    
    repo = FakeBatchRepository(seeded)
    notification_port = AsyncMock()
    
    use_case = ComputeFlakyScoresUseCase(repo, notification_port)
    
    watermark = datetime.utcnow() - timedelta(hours=1)
    processed = await use_case.execute(watermark)
    
    assert processed == 4
    
    # Assertions on upserted records
    results_by_id = {r.test_case_id: r for r in repo.upserted}
    
    # tc-pass should have 0 score
    assert results_by_id["tc-pass"].confidence_adjusted_score == 0.0
    
    # tc-fail should have 0 score (it's consistently broken, not flaky)
    assert results_by_id["tc-fail"].confidence_adjusted_score == 0.0
    
    # tc-alt should have a very high adjusted score (> 0.9)
    assert results_by_id["tc-alt"].flip_rate == 1.0
    assert results_by_id["tc-alt"].confidence_adjusted_score > 0.9
    
    # tc-rare should have a very low adjusted score, well below threshold
    assert results_by_id["tc-rare"].confidence_adjusted_score < 0.1
    
    # Verify Notification Port was called ONLY for the test that crossed threshold (tc-alt)
    assert notification_port.emit_flaky_flagged_event.call_count == 1
    notification_port.emit_flaky_flagged_event.assert_called_with("tc-alt", results_by_id["tc-alt"].confidence_adjusted_score)
