from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class RepositoryRef:
    id: str
    owner: str
    name: str
    provider: str # "github", "gitlab"
    clone_url: str
    webhook_secret: Optional[str] = None

@dataclass
class Commit:
    sha: str
    message: str
    author_name: str
    author_email: str
    timestamp: datetime
    files_changed: List[str]
    additions: int = 0
    deletions: int = 0
    orphaned: bool = False # Used for rewritten history

@dataclass
class FileDiff:
    file_path: str
    status: str # "added", "modified", "removed", "renamed"
    patch: str
    additions: int
    deletions: int
    previous_path: Optional[str] = None
