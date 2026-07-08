from typing import Protocol, List
from datetime import datetime
from services.analytics_batch.domain.entities import FlakyScoreResult

class BatchRepositoryPort(Protocol):
    async def get_test_cases_with_new_executions(self, since: datetime) -> List[str]:
        ...
        
    async def get_execution_outcomes_ordered(self, test_case_id: str, days_back: int = 30) -> List[str]:
        ...
        
    async def get_repository_id_for_test(self, test_case_id: str) -> str:
        ...
        
    async def upsert_flaky_score(self, result: FlakyScoreResult) -> None:
        ...

class NotificationPort(Protocol):
    async def emit_flaky_flagged_event(self, test_case_id: str, score: float) -> None:
        ...
