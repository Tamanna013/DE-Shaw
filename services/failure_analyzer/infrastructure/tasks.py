import asyncio
from services.failure_analyzer.infrastructure.celery_app import celery_app
from services.failure_analyzer.application.use_cases.analyze_failure import AnalyzeFailureUseCase
from shared.logging_engine import get_logger

logger = get_logger(__name__)

# Mock Ports for Task (In a real app, these hit real HTTP APIs or DBs)
class MockLockManager:
    async def acquire_lock(self, key: str, ttl_seconds: int = 300) -> bool: return True
    async def release_lock(self, key: str) -> None: pass

class MockLogParser:
    async def fetch_and_parse(self, execution_id: str) -> dict: return {"stderr": "Mock stack trace"}

class MockStackTraceParser:
    async def parse(self, raw: str) -> dict: return {"frames": [{"file_path": "src/main.py", "is_external": False}]}

class MockCommitAnalyzer:
    async def get_commits_since_last_pass(self, execution_id: str) -> list: return [{"sha": "123", "message": "fix", "files_changed": ["src/main.py"]}]

class MockFailureHistoryRepo:
    async def get_test_case_history(self, tc: str, days: int) -> dict: return {"passes": 1, "fails": 9}
    async def get_execution_status(self, ex: str) -> str: return "failed"
    async def get_cached_report(self, ex: str): return None
    async def save_report(self, rep): pass
    async def save_outbox_event(self, t, p): pass

class MockAIReasoner:
    async def analyze_context(self, ctx: dict) -> list: return []

@celery_app.task(bind=True, max_retries=3)
def analyze_failure_task(self, execution_id: str, test_case_id: str, force: bool = False):
    """
    Background Celery task for failure analysis.
    Uses exponential backoff for infra errors (handled manually or via retry context).
    """
    logger.info("Executing Celery Task: analyze_failure_task", execution_id=execution_id)
    
    use_case = AnalyzeFailureUseCase(
        log_parser=MockLogParser(),
        stack_trace_parser=MockStackTraceParser(),
        commit_analyzer=MockCommitAnalyzer(),
        history_repo=MockFailureHistoryRepo(),
        ai_reasoner=MockAIReasoner(),
        lock_manager=MockLockManager()
    )
    
    try:
        # Celery 5.x doesn't fully support async task defs natively without some hacks,
        # so we use asyncio.run to execute the async use case.
        loop = asyncio.get_event_loop()
        report = loop.run_until_complete(use_case.execute(execution_id, test_case_id, force))
        return {"status": "success", "execution_id": execution_id}
    except Exception as exc:
        # Infra vs Domain error split
        # We would check type of exc here; for mock, assume it's transient and retry
        logger.warning("Task failed, retrying...", exc_info=exc)
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
