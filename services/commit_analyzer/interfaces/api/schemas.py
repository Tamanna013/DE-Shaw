from pydantic import BaseModel
from typing import List

class CandidateCommitSchema(BaseModel):
    sha: str
    message: str
    files_changed: List[str]
    distance_from_head: int

class StackFrameSchema(BaseModel):
    file_path: str
    is_external: bool

class AnalyzeCommitsRequest(BaseModel):
    test_case_id: str
    candidate_commits: List[CandidateCommitSchema]
    stack_frames: List[StackFrameSchema]

class CorrelationSignalSchema(BaseModel):
    file_overlap_score: float
    proximity_score: float
    historical_score: float

class CommitCorrelationSchema(BaseModel):
    commit_sha: str
    commit_message: str
    composite_score: float
    signals: CorrelationSignalSchema
    reason_code: str

class AnalyzeCommitsResponse(BaseModel):
    correlations: List[CommitCorrelationSchema]
