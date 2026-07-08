from dataclasses import dataclass
from typing import List

@dataclass
class CorrelationSignal:
    file_overlap_score: float
    proximity_score: float
    historical_score: float

@dataclass
class CommitCorrelation:
    commit_sha: str
    commit_message: str
    composite_score: float
    signals: CorrelationSignal
    reason_code: str = "ranked"

@dataclass
class CandidateCommit:
    sha: str
    message: str
    files_changed: List[str]
    distance_from_head: int

@dataclass
class StackFrame:
    file_path: str
    is_external: bool
