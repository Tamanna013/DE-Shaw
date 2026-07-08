from typing import List
from services.git_integration.domain.entities import FileDiff, RepositoryRef
from services.git_integration.domain.exceptions import ProviderAPIError
from services.git_integration.application.ports import GitProviderAdapterPort, LocalMirrorPort
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class FetchDiffBetweenShasUseCase:
    def __init__(self, provider: GitProviderAdapterPort, local_mirror: LocalMirrorPort):
        self.provider = provider
        self.local_mirror = local_mirror
        self.rate_limit_threshold = 100

    async def execute(self, repo: RepositoryRef, base_sha: str, head_sha: str) -> List[FileDiff]:
        try:
            remaining = await self.provider.get_rate_limit_remaining()
        except Exception:
            remaining = 9999
            
        if remaining < self.rate_limit_threshold:
            logger.warning(f"Rate limit low ({remaining}). Switching to local mirror for diff.", base=base_sha, head=head_sha)
            await self.local_mirror.ensure_cloned(repo)
            return await self.local_mirror.fetch_diff(repo, base_sha, head_sha)

        try:
            # Accumulate paginated diffs
            all_diffs = []
            page = 1
            per_page = 100
            while True:
                diffs = await self.provider.fetch_diff(repo, base_sha, head_sha, page, per_page)
                if not diffs:
                    break
                all_diffs.extend(diffs)
                
                # Safeguard against infinitely massive diffs blowing up memory (max 1000 files)
                if len(all_diffs) >= 1000:
                    logger.warning("Diff exceeded 1000 files, truncating.", repo=repo.id)
                    break
                    
                if len(diffs) < per_page:
                    break
                page += 1
                
            return all_diffs
        except ProviderAPIError as e:
            logger.warning(f"API diff fetch failed, falling back to local mirror. Status: {e.status_code}", exc_info=e)
            await self.local_mirror.ensure_cloned(repo)
            return await self.local_mirror.fetch_diff(repo, base_sha, head_sha)
