from typing import Protocol, List, Optional
from services.git_integration.domain.entities import Commit, FileDiff, RepositoryRef

class GitProviderAdapterPort(Protocol):
    def provider_name(self) -> str:
        ...

    async def fetch_commit(self, repo: RepositoryRef, sha: str) -> Commit:
        ...

    async def fetch_diff(self, repo: RepositoryRef, base_sha: str, head_sha: str, page: int = 1, per_page: int = 100) -> List[FileDiff]:
        ...

    async def fetch_file_content(self, repo: RepositoryRef, sha: str, file_path: str) -> str:
        ...

    async def get_rate_limit_remaining(self) -> int:
        ...

class LocalMirrorPort(Protocol):
    async def ensure_cloned(self, repo: RepositoryRef) -> None:
        """Ensures a shallow clone exists locally and is up to date."""
        ...

    async def fetch_commit(self, repo: RepositoryRef, sha: str) -> Commit:
        ...

    async def fetch_diff(self, repo: RepositoryRef, base_sha: str, head_sha: str) -> List[FileDiff]:
        ...

    async def fetch_file_content(self, repo: RepositoryRef, sha: str, file_path: str) -> str:
        ...
        
class WebhookTaskQueuePort(Protocol):
    async def enqueue_push_event(self, repo_id: str, shas: List[str], ref: str) -> None:
        ...
