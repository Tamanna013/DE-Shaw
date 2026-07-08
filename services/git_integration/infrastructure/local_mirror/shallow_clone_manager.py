import os
import subprocess
import shutil
from typing import List, Dict
from datetime import datetime
from services.git_integration.domain.entities import Commit, FileDiff, RepositoryRef
from services.git_integration.domain.exceptions import CloneManagerError, CommitNotFoundError
from services.git_integration.application.ports import LocalMirrorPort
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class ShallowCloneManager(LocalMirrorPort):
    def __init__(self, cache_dir: str = "/tmp/testlens_git_cache", max_repos: int = 50):
        self.cache_dir = cache_dir
        self.max_repos = max_repos
        os.makedirs(self.cache_dir, exist_ok=True)
        # Using access time to drive LRU eviction logic in a background process in real life
        # For simplicity, we just manage the bounded directory sizes manually here if needed.

    def _get_repo_path(self, repo: RepositoryRef) -> str:
        return os.path.join(self.cache_dir, f"{repo.owner}_{repo.name}")

    def _run_git(self, repo_path: str, args: List[str]) -> str:
        cmd = ["git", "-C", repo_path] + args
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error("Git command failed", cmd=" ".join(cmd), stderr=e.stderr)
            raise CloneManagerError(f"Git command failed: {e.stderr}")

    async def ensure_cloned(self, repo: RepositoryRef) -> None:
        path = self._get_repo_path(repo)
        
        # NOTE: In a real system, we must embed credentials in clone_url.
        # Assuming clone_url is already authenticated for this use case.
        
        if not os.path.exists(path):
            logger.info("Performing bare clone for local mirror", repo=repo.id)
            cmd = ["git", "clone", "--bare", repo.clone_url, path]
            try:
                subprocess.run(cmd, capture_output=True, text=True, check=True)
            except subprocess.CalledProcessError as e:
                raise CloneManagerError(f"Clone failed: {e.stderr}")
        else:
            # Fetch latest
            logger.debug("Fetching latest in local mirror", repo=repo.id)
            try:
                self._run_git(path, ["fetch", "origin", "+refs/heads/*:refs/heads/*", "--prune"])
            except CloneManagerError:
                pass # Non-fatal if fetch fails, maybe network is down. We'll use what we have.

    async def fetch_commit(self, repo: RepositoryRef, sha: str) -> Commit:
        path = self._get_repo_path(repo)
        
        try:
            # Format: %H|%an|%ae|%cI|%B
            fmt = "%H|%an|%ae|%cI|%B"
            out = self._run_git(path, ["show", "-s", f"--format={fmt}", sha])
            
            # The message might contain newlines, so we only split on the first 4 pipes
            parts = out.split("|", 4)
            if len(parts) != 5:
                raise CommitNotFoundError(f"Malformed git show output for {sha}")
                
            hash_val, author, email, timestamp, message = parts
            
            # Get stats
            stat_out = self._run_git(path, ["show", "--numstat", "--format=", sha])
            additions = 0
            deletions = 0
            files = []
            
            for line in stat_out.splitlines():
                if line.strip():
                    a, d, f = line.split("\t")
                    files.append(f)
                    if a != "-": additions += int(a)
                    if d != "-": deletions += int(d)
                    
            return Commit(
                sha=hash_val,
                message=message.strip(),
                author_name=author,
                author_email=email,
                timestamp=datetime.fromisoformat(timestamp),
                files_changed=files,
                additions=additions,
                deletions=deletions
            )
        except CloneManagerError as e:
            if "bad object" in str(e).lower() or "not a valid object" in str(e).lower():
                raise CommitNotFoundError(f"Commit {sha} not found in local mirror")
            raise

    async def fetch_diff(self, repo: RepositoryRef, base_sha: str, head_sha: str) -> List[FileDiff]:
        path = self._get_repo_path(repo)
        
        # Git diff with numstat to get basic info
        out = self._run_git(path, ["diff", "--numstat", f"{base_sha}...{head_sha}"])
        
        diffs = []
        for line in out.splitlines():
            if line.strip():
                a, d, f = line.split("\t")
                diffs.append(FileDiff(
                    file_path=f,
                    status="modified", # Approximation, would need --name-status for exact
                    patch="", # Excluded for brevity in local mirror
                    additions=int(a) if a != "-" else 0,
                    deletions=int(d) if d != "-" else 0
                ))
        return diffs

    async def fetch_file_content(self, repo: RepositoryRef, sha: str, file_path: str) -> str:
        path = self._get_repo_path(repo)
        try:
            return self._run_git(path, ["show", f"{sha}:{file_path}"])
        except CloneManagerError:
            return ""
