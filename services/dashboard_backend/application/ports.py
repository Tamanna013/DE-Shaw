from typing import Protocol, List
from datetime import datetime
from services.dashboard_backend.domain.entities import (
    FailureTrendSeries, 
    FlakyLeaderboardEntry,
    TeamHealthSummary,
    RepositoryHealth
)

class AnalyticsRepositoryPort(Protocol):
    async def get_failure_trends(self, repository_id: str, from_date: datetime, to_date: datetime, granularity: str) -> FailureTrendSeries:
        ...

    async def get_flaky_leaderboard(self, repository_id: str, limit: int) -> List[FlakyLeaderboardEntry]:
        ...

    async def get_team_health_summary(self, team_id: str) -> TeamHealthSummary:
        ...

    async def get_repository_health(self, repository_id: str) -> RepositoryHealth:
        ...
