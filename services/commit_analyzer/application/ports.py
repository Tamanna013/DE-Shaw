from typing import Protocol, List
from services.commit_analyzer.domain.entities import CommitCorrelation, CandidateCommit

class HistoricalCorrelationRepositoryPort(Protocol):
    async def get_historical_score_for_files(self, test_case_id: str, files_changed: List[str]) -> float:
        """Returns aggregated historical correlation score (0.0 to 1.0)"""
        ...
        
    async def update_baseline(self, test_case_id: str, file_path: str, fails_caused: int) -> None:
        """Batch job update hook"""
        ...

class CommitAnalyzerPort(Protocol):
    # This is what Failure Analyzer will consume
    async def analyze_commits(self, test_case_id: str, candidate_commits: List[CandidateCommit], stack_frames: List[dict]) -> List[CommitCorrelation]:
        ...
