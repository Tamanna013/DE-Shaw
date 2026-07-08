from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ReasonAboutFailureRequest(BaseModel):
    execution_id: str
    test_case_id: str
    log_excerpt: Optional[str]
    stack_trace: Optional[Dict[str, Any]]
    flaky_signal: Optional[Dict[str, Any]]
    commits: List[Dict[str, Any]] = []

class EvidenceReferenceSchema(BaseModel):
    type: str
    ref_id: str

class RecommendedActionSchema(BaseModel):
    action_type: str
    description: str

class RootCauseHypothesisSchema(BaseModel):
    title: str
    description: str
    confidence: str
    score: float
    recommended_actions: List[RecommendedActionSchema]
    evidence_refs: List[EvidenceReferenceSchema]

class ReasonAboutFailureResponse(BaseModel):
    execution_id: str
    hypotheses: List[RootCauseHypothesisSchema]
