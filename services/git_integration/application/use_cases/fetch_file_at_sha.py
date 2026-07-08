from services.git_integration.domain.entities import RepositoryRef
from services.git_integration.domain.exceptions import ProviderAPIError
from services.git_integration.application.ports import GitProviderAdapterPort, LocalMirrorPort
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class FetchFileAtShaUseCase:
    def __init__(self, provider: GitProviderAdapterPort, local_mirror: LocalMirrorPort):
        self.provider = provider
        self.local_mirror = local_mirror
        self.rate_limit_threshold = 100

    async def execute(self, repo: RepositoryRef, sha: str, file_path: str) -> str:
        try:
            remaining = await self.provider.get_rate_limit_remaining()
        except Exception:
            remaining = 9999
            
        if remaining < self.rate_limit_threshold:
            logger.warning(f"Rate limit low ({remaining}). Switching to local mirror for file fetch.", sha=sha, file_path=file_path)
            await self.local_mirror.ensure_cloned(repo)
            return await self.local_mirror.fetch_file_content(repo, sha, file_path)

        try:
            return await self.provider.fetch_file_content(repo, sha, file_path)
        except ProviderAPIError as e:
            logger.warning(f"API file fetch failed, falling back to local mirror. Status: {e.status_code}", exc_info=e)
            await self.local_mirror.ensure_cloned(repo)
            return await self.local_mirror.fetch_file_content(repo, sha, file_path)
