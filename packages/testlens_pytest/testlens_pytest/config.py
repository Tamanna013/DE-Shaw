import os
from typing import Optional

class Config:
    def __init__(self):
        # We read from env vars primarily, but could be extended to read pytest.ini
        self.api_key: Optional[str] = os.environ.get("TESTLENS_API_KEY")
        self.repo_id: Optional[str] = os.environ.get("TESTLENS_REPO_ID", "default_repo")
        self.endpoint: str = os.environ.get("TESTLENS_ENDPOINT", "https://api.testlens.io/v1/ingest/pytest")
        self.batch_size: int = int(os.environ.get("TESTLENS_BATCH_SIZE", "20"))
        self.max_output_size: int = int(os.environ.get("TESTLENS_MAX_OUTPUT_SIZE", "100000")) # 100KB default
        
    @property
    def is_enabled(self) -> bool:
        return bool(self.api_key)

config = Config()
