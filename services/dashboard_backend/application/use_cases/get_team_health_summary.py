from services.dashboard_backend.domain.entities import TeamHealthSummary
from services.dashboard_backend.application.ports import AnalyticsRepositoryPort
from shared.caching.decorators import cached
from shared.caching.cache_client import CacheClient

class GetTeamHealthSummaryUseCase:
    def __init__(self, repo: AnalyticsRepositoryPort, cache_client: CacheClient):
        self.repo = repo
        self.cache_client = cache_client

    @cached(
        cache_client=lambda self: self.cache_client, 
        ttl=600, # 10 minutes for team health
        key_builder=lambda self, team_id: f"testlens:v1:dashboard:team_health:{team_id}"
    )
    async def execute(self, team_id: str) -> dict:
        result = await self.repo.get_team_health_summary(team_id)
        
        return {
            "team_id": result.team_id,
            "total_repositories_owned": result.total_repositories_owned,
            "average_pass_rate": result.average_pass_rate,
            "top_failing_tests": result.top_failing_tests
        }
