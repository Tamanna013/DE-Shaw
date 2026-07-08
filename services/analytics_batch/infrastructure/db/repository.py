from typing import List
from datetime import datetime
from services.analytics_batch.application.ports import BatchRepositoryPort, NotificationPort
from services.analytics_batch.domain.entities import FlakyScoreResult
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class DbBatchRepository(BatchRepositoryPort):
    def __init__(self, session):
        self.session = session

    async def get_test_cases_with_new_executions(self, since: datetime) -> List[str]:
        # Returns test case IDs that have executions newer than 'since'
        return ["tc-123", "tc-456"]

    async def get_execution_outcomes_ordered(self, test_case_id: str, days_back: int = 30) -> List[str]:
        # Would do: SELECT outcome FROM test_case_executions WHERE test_case_id = :id AND created_at > :days_back ORDER BY created_at ASC
        return ["passed", "failed", "passed"]
        
    async def get_repository_id_for_test(self, test_case_id: str) -> str:
        return "repo-1"

    async def upsert_flaky_score(self, result: FlakyScoreResult) -> None:
        # Would do an INSERT ... ON CONFLICT (test_case_id) DO UPDATE SET flaky_score = EXCLUDED.flaky_score
        logger.info(f"Upserting flaky score for {result.test_case_id}: {result.confidence_adjusted_score}")

class ApiNotificationPort(NotificationPort):
    async def emit_flaky_flagged_event(self, test_case_id: str, score: float) -> None:
        logger.info(f"FLAGGED FLAKY: {test_case_id} crossed threshold with score {score}")
