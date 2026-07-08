from typing import List
from services.dashboard_backend.domain.entities import FlakyLeaderboardEntry
from services.dashboard_backend.application.ports import AnalyticsRepositoryPort
from shared.caching.decorators import cached
from shared.caching.cache_client import CacheClient

class GetFlakyLeaderboardUseCase:
    def __init__(self, repo: AnalyticsRepositoryPort, cache_client: CacheClient):
        self.repo = repo
        self.cache_client = cache_client

    @cached(
        cache_client=lambda self: self.cache_client, 
        ttl=300, 
        key_builder=lambda self, repo_id, limit: f"testlens:v1:dashboard:leaderboard:flaky:{repo_id}:{limit}"
    )
    async def execute(self, repository_id: str, limit: int) -> List[dict]:
        limit = min(limit, 100) # Hard cap at 100
        
        results = await self.repo.get_flaky_leaderboard(repository_id, limit)
        return [
            {
                "test_case_id": r.test_case_id,
                "test_case_name": r.test_case_name,
                "flaky_score": r.flaky_score,
                "flip_count": r.flip_count
            } for r in results
        ]
