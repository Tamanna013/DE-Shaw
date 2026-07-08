from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AnalyzeFailureRequest(BaseModel):
    test_case_id: str
    force: bool = False

class RecommendedActionSchema(BaseModel):
    action_type: str
    description: str

class RootCauseHypothesisSchema(BaseModel):
    title: str
    description: str
    confidence: str
    score: float
    recommended_actions: List[RecommendedActionSchema]
    related_commit_shas: List[str]

class FailureAnalysisReportResponse(BaseModel):
    execution_id: str
    test_case_id: str
    analyzed_at: datetime
    ai_reasoning_status: str
    flaky_signal_score: float
    context_bundle_summary: str
    hypotheses: List[RootCauseHypothesisSchema]
