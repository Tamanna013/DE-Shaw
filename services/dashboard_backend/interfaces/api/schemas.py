from pydantic import BaseModel
from typing import List
from datetime import datetime

class TrendPointSchema(BaseModel):
    timestamp: str
    total_executions: int
    total_failures: int
    failure_rate: float

class FailureTrendSeriesSchema(BaseModel):
    repository_id: str
    granularity: str
    data_points: List[TrendPointSchema]

class FlakyLeaderboardEntrySchema(BaseModel):
    test_case_id: str
    test_case_name: str
    flaky_score: float
    flip_count: int

class TeamHealthSummarySchema(BaseModel):
    team_id: str
    total_repositories_owned: int
    average_pass_rate: float
    top_failing_tests: List[str]

class RepositoryHealthSchema(BaseModel):
    repository_id: str
    overall_pass_rate: float
    avg_ci_latency_seconds: float
    total_test_cases: int
