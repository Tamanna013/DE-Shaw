import os
import httpx
from datetime import datetime
from typing import List
from services.git_integration.domain.entities import Commit, FileDiff, RepositoryRef
from services.git_integration.domain.exceptions import ProviderAPIError
from services.git_integration.application.ports import GitProviderAdapterPort

class GitHubAdapter(GitProviderAdapterPort):
    def __init__(self):
        # We assume PAT auth for simplicity here, but would use App auth if configured.
        self.api_key = os.environ.get("GITHUB_TOKEN", "")
        self.base_url = "https://api.github.com"
        
        # Internal cache of rate limit to avoid extra calls
        self._rate_limit_remaining = 5000

    def provider_name(self) -> str:
        return "github"
        
    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
    def _update_rate_limit(self, resp: httpx.Response):
        if "X-RateLimit-Remaining" in resp.headers:
            self._rate_limit_remaining = int(resp.headers["X-RateLimit-Remaining"])

    async def fetch_commit(self, repo: RepositoryRef, sha: str) -> Commit:
        url = f"{self.base_url}/repos/{repo.owner}/{repo.name}/commits/{sha}"
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self._headers())
            self._update_rate_limit(resp)
            
            if resp.status_code == 404:
                raise ProviderAPIError(f"Commit {sha} not found (force-pushed?)", status_code=404, rate_limit_remaining=self._rate_limit_remaining)
            elif resp.status_code != 200:
                raise ProviderAPIError(f"GitHub API Error: {resp.text}", status_code=resp.status_code, rate_limit_remaining=self._rate_limit_remaining)
                
            data = resp.json()
            
            files = data.get("files", [])
            file_paths = [f["filename"] for f in files]
            additions = data.get("stats", {}).get("additions", 0)
            deletions = data.get("stats", {}).get("deletions", 0)
            
            return Commit(
                sha=data["sha"],
                message=data["commit"]["message"],
                author_name=data["commit"]["author"]["name"],
                author_email=data["commit"]["author"]["email"],
                timestamp=datetime.fromisoformat(data["commit"]["author"]["date"].replace("Z", "+00:00")),
                files_changed=file_paths,
                additions=additions,
                deletions=deletions
            )

    async def fetch_diff(self, repo: RepositoryRef, base_sha: str, head_sha: str, page: int = 1, per_page: int = 100) -> List[FileDiff]:
        # Note: GitHub compares base...head
        url = f"{self.base_url}/repos/{repo.owner}/{repo.name}/compare/{base_sha}...{head_sha}"
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params={"page": page, "per_page": per_page}, headers=self._headers())
            self._update_rate_limit(resp)
            
            if resp.status_code != 200:
                raise ProviderAPIError(f"GitHub API Error: {resp.text}", status_code=resp.status_code, rate_limit_remaining=self._rate_limit_remaining)
                
            data = resp.json()
            
            diffs = []
            for f in data.get("files", []):
                diffs.append(FileDiff(
                    file_path=f["filename"],
                    status=f["status"],
                    patch=f.get("patch", ""), # Binary files might not have patch
                    additions=f.get("additions", 0),
                    deletions=f.get("deletions", 0),
                    previous_path=f.get("previous_filename")
                ))
            return diffs

    async def fetch_file_content(self, repo: RepositoryRef, sha: str, file_path: str) -> str:
        # Using raw header to get plain text
        url = f"{self.base_url}/repos/{repo.owner}/{repo.name}/contents/{file_path}"
        headers = self._headers()
        headers["Accept"] = "application/vnd.github.v3.raw"
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params={"ref": sha}, headers=headers)
            self._update_rate_limit(resp)
            
            if resp.status_code != 200:
                raise ProviderAPIError(f"GitHub API Error: {resp.text}", status_code=resp.status_code, rate_limit_remaining=self._rate_limit_remaining)
                
            return resp.text

    async def get_rate_limit_remaining(self) -> int:
        return self._rate_limit_remaining
