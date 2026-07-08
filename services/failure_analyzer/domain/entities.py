from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from datetime import datetime

class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass
class RecommendedAction:
    action_type: str
    description: str

@dataclass
class RootCauseHypothesis:
    title: str
    description: str
    confidence: ConfidenceLevel
    score: float # 0.0 to 1.0
    recommended_actions: List[RecommendedAction] = field(default_factory=list)
    related_commit_shas: List[str] = field(default_factory=list)

@dataclass
class FailureAnalysisReport:
    execution_id: str
    test_case_id: str
    analyzed_at: datetime
    ai_reasoning_status: str # "completed", "failed"
    hypotheses: List[RootCauseHypothesis]
    flaky_signal_score: float
    context_bundle_summary: str
    
    # Optional fields for partial persistence
    id: Optional[str] = None
