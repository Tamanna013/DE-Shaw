import httpx
import logging
from typing import List
from testlens_pytest.models import TestResultPayload

# Note: local-only logging, respects customer log level
logger = logging.getLogger("testlens_pytest")

class TestLensClient:
    def __init__(self, api_key: str, repo_id: str, endpoint: str):
        self.api_key = api_key
        self.repo_id = repo_id
        self.endpoint = endpoint
        # Use sync client for pytest plugin to avoid async event loop complexities in a pure hook
        # Pytest is fundamentally synchronous. Using an async client in a synchronous hook
        # would require spinning up an event loop, which can conflict with plugins like pytest-asyncio.
        # Fire-and-forget is handled via timeouts and short circuiting.
        self.client = httpx.Client(timeout=3.0) 

    def flush_batch(self, batch: List[TestResultPayload]) -> None:
        if not batch:
            return
            
        payload = {
            "repo_id": self.repo_id,
            "results": [result.model_dump() for result in batch]
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            # 1 retry logic is built in here manually
            resp = self.client.post(self.endpoint, json=payload, headers=headers)
            if resp.status_code >= 500:
                # Retry once on 5xx
                resp = self.client.post(self.endpoint, json=payload, headers=headers)
                resp.raise_for_status()
            else:
                resp.raise_for_status()
                
        except Exception as e:
            # NEVER fail the test run. Drop the payload and log a warning.
            logger.warning(f"TestLens ingest failed: {e}. Dropping batch of {len(batch)} results.")
