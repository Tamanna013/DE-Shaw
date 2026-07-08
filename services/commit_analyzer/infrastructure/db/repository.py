from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from services.commit_analyzer.application.ports import HistoricalCorrelationRepositoryPort
from services.commit_analyzer.infrastructure.db.models import CommitTestCorrelationModel

class DbHistoricalCorrelationRepository(HistoricalCorrelationRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_historical_score_for_files(self, test_case_id: str, files_changed: List[str]) -> float:
        if not files_changed:
            return 0.0
            
        # For a given test and list of files, we find the max historical score.
        stmt = select(CommitTestCorrelationModel.historical_score_cached).where(
            CommitTestCorrelationModel.test_case_id == test_case_id,
            CommitTestCorrelationModel.file_path.in_(files_changed)
        )
        result = await self.session.execute(stmt)
        scores = result.scalars().all()
        
        if not scores:
            return 0.0
            
        return max(scores)

    async def update_baseline(self, test_case_id: str, file_path: str, fails_caused: int) -> None:
        # Implementation for batch job
        pass
