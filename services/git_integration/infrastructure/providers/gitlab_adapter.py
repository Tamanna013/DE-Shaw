import os
import httpx
from datetime import datetime
from typing import List
from services.git_integration.domain.entities import Commit, FileDiff, RepositoryRef
from services.git_integration.domain.exceptions import ProviderAPIError
from services.git_integration.application.ports import GitProviderAdapterPort

class GitLabAdapter(GitProviderAdapterPort):
    def __init__(self):
        self.api_key = os.environ.get("GITLAB_TOKEN", "")
        self.base_url = "https://gitlab.com/api/v4"
        self._rate_limit_remaining = 5000

    def provider_name(self) -> str:
        return "gitlab"
        
    def _headers(self):
        return {
            "PRIVATE-TOKEN": self.api_key
        }

    async def fetch_commit(self, repo: RepositoryRef, sha: str) -> Commit:
        # GitLab expects URL-encoded project path
        project_path = f"{repo.owner}%2F{repo.name}"
        url = f"{self.base_url}/projects/{project_path}/repository/commits/{sha}"
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self._headers())
            
            if resp.status_code == 404:
                raise ProviderAPIError(f"Commit not found", status_code=404)
            elif resp.status_code != 200:
                raise ProviderAPIError(f"GitLab API Error: {resp.text}", status_code=resp.status_code)
                
            data = resp.json()
            
            # GitLab requires a separate API call to get diff/stats if we want full file list,
            # but for this mock adapter we'll just return basic info to satisfy interface.
            return Commit(
                sha=data["id"],
                message=data["message"],
                author_name=data["author_name"],
                author_email=data["author_email"],
                timestamp=datetime.fromisoformat(data["created_at"]),
                files_changed=[], 
                additions=0,
                deletions=0
            )

    async def fetch_diff(self, repo: RepositoryRef, base_sha: str, head_sha: str, page: int = 1, per_page: int = 100) -> List[FileDiff]:
        # Stub implementation
        return []

    async def fetch_file_content(self, repo: RepositoryRef, sha: str, file_path: str) -> str:
        # Stub implementation
        return ""

    async def get_rate_limit_remaining(self) -> int:
        return self._rate_limit_remaining
