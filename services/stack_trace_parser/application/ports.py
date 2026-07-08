from typing import Protocol, Optional

class SourceCodeFetcherPort(Protocol):
    async def fetch_context(self, commit_sha: str, file_path: str, line_number: int, context_lines: int = 3) -> Optional[str]:
        """Fetches the source code context around a given line via Git Integration."""
        ...
