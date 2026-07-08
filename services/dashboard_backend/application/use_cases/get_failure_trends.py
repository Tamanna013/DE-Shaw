from datetime import datetime, timedelta
from services.dashboard_backend.domain.entities import FailureTrendSeries
from services.dashboard_backend.domain.exceptions import InvalidDateRangeError
from services.dashboard_backend.application.ports import AnalyticsRepositoryPort
from shared.caching.decorators import cached
from shared.caching.cache_client import CacheClient

class GetFailureTrendsUseCase:
    def __init__(self, repo: AnalyticsRepositoryPort, cache_client: CacheClient):
        self.repo = repo
        self.cache_client = cache_client

    def _validate_date_range(self, from_date: datetime, to_date: datetime):
        if to_date < from_date:
            raise InvalidDateRangeError("to_date cannot be earlier than from_date")
        if (to_date - from_date) > timedelta(days=365):
            raise InvalidDateRangeError("Date range capped at 1 year to bound query cost. Use a coarser granularity or shorter range.")

    @cached(
        cache_client=lambda self: self.cache_client, 
        ttl=300, 
        key_builder=lambda self, repo_id, from_date, to_date, granularity: f"testlens:v1:dashboard:trends:{repo_id}:{from_date.isoformat()}:{to_date.isoformat()}:{granularity}"
    )
    async def execute(self, repository_id: str, from_date: datetime, to_date: datetime, granularity: str) -> dict:
        self._validate_date_range(from_date, to_date)
        
        if granularity not in ["day", "week", "month"]:
            raise ValueError(f"Invalid granularity: {granularity}")
            
        result = await self.repo.get_failure_trends(repository_id, from_date, to_date, granularity)
        
        # Serialization for caching
        return {
            "repository_id": result.repository_id,
            "granularity": result.granularity,
            "data_points": [
                {
                    "timestamp": p.timestamp,
                    "total_executions": p.total_executions,
                    "total_failures": p.total_failures,
                    "failure_rate": p.failure_rate
                } for p in result.data_points
            ]
        }
