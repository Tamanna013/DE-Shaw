from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any

class ConfidenceScore(float):
    """A bounded float between 0.0 and 1.0"""
    pass

class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass
class RecommendedAction:
    action_type: str
    description: str

@dataclass
class EvidenceReference:
    type: str # "historical_failure", "commit", "flaky_signal", "heuristic"
    ref_id: str

@dataclass
class RootCauseHypothesis:
    title: str
    description: str
    llm_confidence: float
    confidence: ConfidenceLevel = ConfidenceLevel.LOW
    score: float = 0.0
    recommended_actions: List[RecommendedAction] = field(default_factory=list)
    evidence_refs: List[EvidenceReference] = field(default_factory=list)

@dataclass
class HistoricalFailureInfo:
    id: str
    test_case_id: str
    normalized_signature: str
    similarity_score: float
    resolution_notes: Optional[str] = None

@dataclass
class ReasoningContext:
    execution_id: str
    test_case_id: str
    log_excerpt: Optional[str]
    stack_trace: Optional[Dict[str, Any]]
    flaky_signal: Optional[Dict[str, Any]]
    commits: List[Dict[str, Any]] = field(default_factory=list)
    similar_historical_failures: List[HistoricalFailureInfo] = field(default_factory=list)
