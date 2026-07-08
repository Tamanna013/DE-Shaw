import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from services.failure_analyzer.domain.entities import RootCauseHypothesis, ConfidenceLevel
from services.failure_analyzer.application.use_cases.analyze_failure import AnalyzeFailureUseCase
from services.failure_analyzer.domain.exceptions import ExecutionNotFailedError

@pytest.fixture
def mock_ports():
    log_parser = AsyncMock()
    log_parser.fetch_and_parse.return_value = {"stderr": "Raw stderr output"}
    
    stack_parser = AsyncMock()
    stack_parser.parse.return_value = {"frames": [{"file_path": "src/main.py", "is_external": False}]}
    
    commit_analyzer = AsyncMock()
    commit_analyzer.get_commits_since_last_pass.return_value = [
        {"sha": "123", "message": "Fix bug", "files_changed": ["src/main.py"]},
        {"sha": "456", "message": "Update docs", "files_changed": ["README.md"]}
    ]
    
    history_repo = AsyncMock()
    history_repo.get_execution_status.return_value = "failed"
    history_repo.get_cached_report.return_value = None
    history_repo.get_test_case_history.return_value = {"passes": 1, "fails": 9} # 90% flip rate
    history_repo.save_report = AsyncMock()
    history_repo.save_outbox_event = AsyncMock()
    
    ai_reasoner = AsyncMock()
    ai_reasoner.analyze_context.return_value = [
        RootCauseHypothesis(title="AI Guess", description="Desc", confidence=ConfidenceLevel.MEDIUM, score=0.7)
    ]
    
    lock_manager = AsyncMock()
    lock_manager.acquire_lock.return_value = True
    
    return {
        "log_parser": log_parser,
        "stack_trace_parser": stack_parser,
        "commit_analyzer": commit_analyzer,
        "history_repo": history_repo,
        "ai_reasoner": ai_reasoner,
        "lock_manager": lock_manager
    }

@pytest.mark.asyncio
async def test_analyze_orchestrates_all_stages(mock_ports):
    use_case = AnalyzeFailureUseCase(**mock_ports)
    
    report = await use_case.execute("exec-1", "tc-1")
    
    assert report.execution_id == "exec-1"
    assert report.test_case_id == "tc-1"
    
    # Check that flaky signal was injected because flip rate is 90%
    flaky_hyps = [h for h in report.hypotheses if "Flaky" in h.title]
    assert len(flaky_hyps) == 1
    assert flaky_hyps[0].score == 0.9
    
    # Check save was called
    mock_ports["history_repo"].save_report.assert_called_once()
    mock_ports["history_repo"].save_outbox_event.assert_called_once()

@pytest.mark.asyncio
async def test_execution_not_failed_aborts(mock_ports):
    mock_ports["history_repo"].get_execution_status.return_value = "passed"
    use_case = AnalyzeFailureUseCase(**mock_ports)
    
    with pytest.raises(ExecutionNotFailedError):
        await use_case.execute("exec-1", "tc-1")

@pytest.mark.asyncio
async def test_partial_report_persisted_when_ai_reasoning_times_out(mock_ports):
    # Simulate AI reasoner timing out or throwing exception
    mock_ports["ai_reasoner"].analyze_context.side_effect = asyncio.TimeoutError()
    
    use_case = AnalyzeFailureUseCase(**mock_ports)
    report = await use_case.execute("exec-1", "tc-1")
    
    # AI status should be failed
    assert report.ai_reasoning_status == "failed"
    
    # We should still have the flaky hypothesis injected
    assert len(report.hypotheses) > 0
    assert report.hypotheses[0].title == "Likely Flaky Test or Environment Issue"
