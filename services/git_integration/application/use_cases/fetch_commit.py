from services.git_integration.domain.entities import Commit, RepositoryRef
from services.git_integration.domain.exceptions import ProviderAPIError
from services.git_integration.application.ports import GitProviderAdapterPort, LocalMirrorPort
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class FetchCommitUseCase:
    def __init__(self, provider: GitProviderAdapterPort, local_mirror: LocalMirrorPort):
        self.provider = provider
        self.local_mirror = local_mirror
        self.rate_limit_threshold = 100 # Switch to mirror if < 100 calls left

    async def execute(self, repo: RepositoryRef, sha: str) -> Commit:
        # Check rate limit heuristic
        try:
            remaining = await self.provider.get_rate_limit_remaining()
        except Exception:
            remaining = 9999
            
        if remaining < self.rate_limit_threshold:
            logger.warning(f"Rate limit low ({remaining}). Switching to local mirror for commit fetch.", sha=sha)
            await self.local_mirror.ensure_cloned(repo)
            return await self.local_mirror.fetch_commit(repo, sha)

        # Try API
        try:
            return await self.provider.fetch_commit(repo, sha)
        except ProviderAPIError as e:
            if e.status_code == 404:
                # E.g. force push orphaned it. For sync pipelines, we might still want it if it exists in local mirror
                pass
            logger.warning(f"API fetch failed, falling back to local mirror. Status: {e.status_code}", exc_info=e)
            
            # Fallback to local mirror
            await self.local_mirror.ensure_cloned(repo)
            return await self.local_mirror.fetch_commit(repo, sha)
