from dataclasses import dataclass
from typing import List, Optional

@dataclass
class FlakyScoreResult:
    test_case_id: str
    repository_id: str
    flip_rate: float
    confidence_adjusted_score: float
    flip_count: int
    total_executions: int

@dataclass
class DigestSummary:
    team_id: str
    new_flaky_tests: int
    top_failing_tests: List[str]
    total_failures_prevented: int
