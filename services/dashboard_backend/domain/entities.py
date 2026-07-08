from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class TrendPoint:
    timestamp: str # ISO string truncated to granularity (e.g. YYYY-MM-DD)
    total_executions: int
    total_failures: int
    failure_rate: float

@dataclass
class FailureTrendSeries:
    repository_id: str
    granularity: str
    data_points: List[TrendPoint]

@dataclass
class FlakyLeaderboardEntry:
    test_case_id: str
    test_case_name: str
    flaky_score: float
    flip_count: int

@dataclass
class TeamHealthSummary:
    team_id: str
    total_repositories_owned: int
    average_pass_rate: float
    top_failing_tests: List[str]

@dataclass
class RepositoryHealth:
    repository_id: str
    overall_pass_rate: float
    avg_ci_latency_seconds: float
    total_test_cases: int
