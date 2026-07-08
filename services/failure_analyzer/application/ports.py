from typing import Protocol, List, Optional
from datetime import datetime
from services.failure_analyzer.domain.entities import FailureAnalysisReport, RootCauseHypothesis

class LogParserPort(Protocol):
    async def fetch_and_parse(self, execution_id: str) -> dict:
        ...

class StackTraceParserPort(Protocol):
    async def parse(self, raw_stderr: str) -> dict:
        ...

class CommitAnalyzerPort(Protocol):
    async def get_commits_since_last_pass(self, execution_id: str) -> List[dict]:
        ...

class FailureHistoryRepositoryPort(Protocol):
    async def get_test_case_history(self, test_case_id: str, days: int = 90) -> dict:
        ...
    async def get_execution_status(self, execution_id: str) -> str:
        ...
    async def get_cached_report(self, execution_id: str) -> Optional[FailureAnalysisReport]:
        ...
    async def save_report(self, report: FailureAnalysisReport) -> None:
        ...
    async def save_outbox_event(self, event_type: str, payload: dict) -> None:
        ...

class AIReasoningPort(Protocol):
    async def analyze_context(self, context_bundle: dict) -> List[RootCauseHypothesis]:
        ...

class LockManagerPort(Protocol):
    async def acquire_lock(self, key: str, ttl_seconds: int = 300) -> bool:
        ...
    async def release_lock(self, key: str) -> None:
        ...
