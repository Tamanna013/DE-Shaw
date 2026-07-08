from typing import List
from services.commit_analyzer.domain.entities import CommitCorrelation, CandidateCommit, CorrelationSignal, StackFrame
from services.commit_analyzer.application.ports import HistoricalCorrelationRepositoryPort

# Configurable Weights (could be moved to env vars later)
WEIGHT_FILE_OVERLAP = 0.5
WEIGHT_PROXIMITY = 0.2
WEIGHT_HISTORICAL = 0.3

def compute_file_overlap_score(commit: CandidateCommit, frames: List[StackFrame]) -> float:
    """
    fraction of stack-trace frame file paths that appear in the commit's changed-files list
    weighted higher for frames closer to the top/root of the trace.
    Frames are assumed ordered from top (closest to error) to bottom.
    """
    if not frames or not commit.files_changed:
        return 0.0
        
    score = 0.0
    total_weight = 0.0
    
    commit_files = set(commit.files_changed)
    
    for i, frame in enumerate(frames):
        if frame.is_external:
            continue
            
        # Top frame has highest weight, decaying down the stack
        # e.g., i=0 -> weight=1.0, i=1 -> weight=0.5, etc.
        weight = 1.0 / (i + 1)
        total_weight += weight
        
        if frame.file_path in commit_files:
            score += weight
            
    if total_weight == 0:
        return 0.0
        
    return score / total_weight

def compute_proximity_score(distance: int) -> float:
    """
    inverse of commit distance from HEAD
    1 / (1 + distance * 0.1)
    """
    if distance < 0:
        return 0.0
    return 1.0 / (1.0 + (distance * 0.1))

def compute_composite_score(overlap: float, proximity: float, historical: float) -> float:
    return (overlap * WEIGHT_FILE_OVERLAP) + (proximity * WEIGHT_PROXIMITY) + (historical * WEIGHT_HISTORICAL)

class CorrelateCommitsWithFailureUseCase:
    def __init__(self, repo: HistoricalCorrelationRepositoryPort):
        self.repo = repo

    async def execute(self, test_case_id: str, candidate_commits: List[CandidateCommit], stack_frames_raw: List[dict]) -> List[CommitCorrelation]:
        if not candidate_commits:
            return [CommitCorrelation(
                commit_sha="none",
                commit_message="",
                composite_score=0.0,
                signals=CorrelationSignal(0.0, 0.0, 0.0),
                reason_code="no_commits_in_range"
            )]
            
        frames = [StackFrame(file_path=f.get("file_path", ""), is_external=f.get("is_external", False)) for f in stack_frames_raw]
        
        results = []
        for commit in candidate_commits:
            overlap = compute_file_overlap_score(commit, frames)
            prox = compute_proximity_score(commit.distance_from_head)
            hist = await self.repo.get_historical_score_for_files(test_case_id, commit.files_changed)
            
            comp = compute_composite_score(overlap, prox, hist)
            
            results.append(CommitCorrelation(
                commit_sha=commit.sha,
                commit_message=commit.message,
                composite_score=comp,
                signals=CorrelationSignal(
                    file_overlap_score=overlap,
                    proximity_score=prox,
                    historical_score=hist
                ),
                reason_code="ranked"
            ))
            
        results.sort(key=lambda c: c.composite_score, reverse=True)
        return results
