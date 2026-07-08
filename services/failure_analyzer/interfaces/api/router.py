from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from services.failure_analyzer.interfaces.api.schemas import AnalyzeFailureRequest, FailureAnalysisReportResponse, RootCauseHypothesisSchema, RecommendedActionSchema
from services.failure_analyzer.infrastructure.tasks import analyze_failure_task
from services.failure_analyzer.infrastructure.db.repository import FailureHistoryRepository
from shared.db.session import get_db_session
from shared.logging_engine import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/failures", tags=["failure_analyzer"])

@router.post("/{execution_id}/analyze")
async def trigger_analysis(execution_id: str, req: AnalyzeFailureRequest):
    """
    Triggers an async celery task to analyze the failure. Returns 202 Accepted.
    """
    logger.info("Queuing analysis task", execution_id=execution_id)
    # Fire off to Celery
    analyze_failure_task.delay(execution_id, req.test_case_id, req.force)
    return {"status": "accepted", "execution_id": execution_id, "message": "Analysis queued."}

@router.get("/{execution_id}/report", response_model=FailureAnalysisReportResponse)
async def get_report(execution_id: str, session: AsyncSession = Depends(get_db_session)):
    """
    Fetches a completed report from the database.
    """
    repo = FailureHistoryRepository(session)
    report = await repo.get_cached_report(execution_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found or analysis still in progress")
        
    return FailureAnalysisReportResponse(
        execution_id=report.execution_id,
        test_case_id=report.test_case_id,
        analyzed_at=report.analyzed_at,
        ai_reasoning_status=report.ai_reasoning_status,
        flaky_signal_score=report.flaky_signal_score,
        context_bundle_summary=report.context_bundle_summary,
        hypotheses=[
            RootCauseHypothesisSchema(
                title=h.title,
                description=h.description,
                confidence=h.confidence.value,
                score=h.score,
                recommended_actions=[RecommendedActionSchema(action_type=a.action_type, description=a.description) for a in h.recommended_actions],
                related_commit_shas=h.related_commit_shas
            ) for h in report.hypotheses
        ]
    )
