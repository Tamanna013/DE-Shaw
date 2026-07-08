from services.dashboard_backend.domain.entities import RepositoryHealth
from services.dashboard_backend.application.ports import AnalyticsRepositoryPort
from shared.caching.decorators import cached
from shared.caching.cache_client import CacheClient

class GetRepositoryHealthUseCase:
    def __init__(self, repo: AnalyticsRepositoryPort, cache_client: CacheClient):
        self.repo = repo
        self.cache_client = cache_client

    @cached(
        cache_client=lambda self: self.cache_client, 
        ttl=300, 
        key_builder=lambda self, repo_id: f"testlens:v1:dashboard:repo_health:{repo_id}"
    )
    async def execute(self, repository_id: str) -> dict:
        result = await self.repo.get_repository_health(repository_id)
        
        return {
            "repository_id": result.repository_id,
            "overall_pass_rate": result.overall_pass_rate,
            "avg_ci_latency_seconds": result.avg_ci_latency_seconds,
            "total_test_cases": result.total_test_cases
        }
