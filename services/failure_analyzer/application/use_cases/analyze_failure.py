import asyncio
from datetime import datetime, timezone
from typing import Optional
from services.failure_analyzer.domain.entities import FailureAnalysisReport, RootCauseHypothesis, ConfidenceLevel
from services.failure_analyzer.domain.exceptions import ExecutionNotFailedError, ConcurrentAnalysisInProgressError
from services.failure_analyzer.application.ports import (
    LogParserPort, StackTraceParserPort, CommitAnalyzerPort, 
    FailureHistoryRepositoryPort, AIReasoningPort, LockManagerPort
)
from services.failure_analyzer.application.use_cases.correlate_with_flaky_history import CorrelateWithFlakyHistoryUseCase
from services.failure_analyzer.application.use_cases.correlate_with_recent_commits import CorrelateWithRecentCommitsUseCase
from services.failure_analyzer.application.use_cases.rank_hypotheses import RankHypothesesUseCase
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class AnalyzeFailureUseCase:
    def __init__(self, 
                 log_parser: LogParserPort,
                 stack_trace_parser: StackTraceParserPort,
                 commit_analyzer: CommitAnalyzerPort,
                 history_repo: FailureHistoryRepositoryPort,
                 ai_reasoner: AIReasoningPort,
                 lock_manager: LockManagerPort):
        self.log_parser = log_parser
        self.stack_trace_parser = stack_trace_parser
        self.commit_analyzer = commit_analyzer
        self.history_repo = history_repo
        self.ai_reasoner = ai_reasoner
        self.lock_manager = lock_manager
        
        self.flaky_correlator = CorrelateWithFlakyHistoryUseCase(history_repo)
        self.commit_correlator = CorrelateWithRecentCommitsUseCase(commit_analyzer)
        self.ranker = RankHypothesesUseCase()

    async def execute(self, execution_id: str, test_case_id: str, force: bool = False) -> FailureAnalysisReport:
        logger.info("Starting analysis orchestration", execution_id=execution_id)
        
        status = await self.history_repo.get_execution_status(execution_id)
        if status != "failed":
            raise ExecutionNotFailedError(f"Execution {execution_id} is in status {status}, not failed.")
            
        if not force:
            cached_report = await self.history_repo.get_cached_report(execution_id)
            if cached_report:
                logger.info("Returning cached report", execution_id=execution_id)
                return cached_report
                
        lock_key = f"analysis_lock:{execution_id}"
        acquired = await self.lock_manager.acquire_lock(lock_key, ttl_seconds=60)
        if not acquired:
            raise ConcurrentAnalysisInProgressError("Analysis is already running for this execution")
            
        try:
            # 1 & 2. Parse Log & Stack Trace
            log_data = await self.log_parser.fetch_and_parse(execution_id)
            raw_stderr = log_data.get("stderr", "")
            parsed_stack_trace = await self.stack_trace_parser.parse(raw_stderr)
            
            # 3. Flaky History
            flaky_signal = await self.flaky_correlator.execute(test_case_id)
            
            # 4. Commits
            ranked_commits = await self.commit_correlator.execute(execution_id, parsed_stack_trace)
            
            # 5. Build context bundle
            context_bundle = {
                "execution_id": execution_id,
                "test_case_id": test_case_id,
                "log_excerpt": raw_stderr[-5000:], # limit size
                "stack_trace": parsed_stack_trace,
                "commits": ranked_commits[:5],
                "flaky_signal": flaky_signal
            }
            
            ai_status = "completed"
            ai_hypotheses = []
            try:
                # Max 6s timeout internally handled by adapter, but we wrap in asyncio.wait_for just in case
                ai_hypotheses = await asyncio.wait_for(self.ai_reasoner.analyze_context(context_bundle), timeout=8.0)
            except Exception as e:
                logger.warning("AI Reasoning Engine failed or timed out", exc_info=e)
                ai_status = "failed"
                
            # 6. Rank Hypotheses
            final_hypotheses = self.ranker.execute(ai_hypotheses, flaky_signal, ranked_commits)
            
            # 7. Persist and Publish
            report = FailureAnalysisReport(
                execution_id=execution_id,
                test_case_id=test_case_id,
                analyzed_at=datetime.now(timezone.utc),
                ai_reasoning_status=ai_status,
                hypotheses=final_hypotheses,
                flaky_signal_score=flaky_signal.get("flip_rate", 0.0),
                context_bundle_summary=f"Context parsed. Commits: {len(ranked_commits)}. Flaky: {flaky_signal.get('is_flaky')}"
            )
            
            await self.history_repo.save_report(report)
            
            # Transactional outbox
            await self.history_repo.save_outbox_event("failure.analyzed", {
                "execution_id": execution_id,
                "test_case_id": test_case_id,
                "status": ai_status
            })
            
            logger.info("Analysis complete", execution_id=execution_id)
            return report
            
        finally:
            await self.lock_manager.release_lock(lock_key)
