from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from services.commit_analyzer.interfaces.api.schemas import AnalyzeCommitsRequest, AnalyzeCommitsResponse, CommitCorrelationSchema, CorrelationSignalSchema
from services.commit_analyzer.domain.entities import CandidateCommit
from services.commit_analyzer.application.use_cases.correlate_commits_with_failure import CorrelateCommitsWithFailureUseCase
from services.commit_analyzer.infrastructure.db.repository import DbHistoricalCorrelationRepository
from shared.db.session import get_db_session
from shared.logging_engine import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/commits", tags=["commit_analyzer"])

@router.post("/analyze", response_model=AnalyzeCommitsResponse)
async def analyze_commits(req: AnalyzeCommitsRequest, session: AsyncSession = Depends(get_db_session)):
    repo = DbHistoricalCorrelationRepository(session)
    use_case = CorrelateCommitsWithFailureUseCase(repo)
    
    candidates = [CandidateCommit(**c.__dict__) for c in req.candidate_commits]
    frames = [f.__dict__ for f in req.stack_frames]
    
    correlations = await use_case.execute(req.test_case_id, candidates, frames)
    
    return AnalyzeCommitsResponse(
        correlations=[
            CommitCorrelationSchema(
                commit_sha=c.commit_sha,
                commit_message=c.commit_message,
                composite_score=c.composite_score,
                signals=CorrelationSignalSchema(**c.signals.__dict__),
                reason_code=c.reason_code
            ) for c in correlations
        ]
    )
