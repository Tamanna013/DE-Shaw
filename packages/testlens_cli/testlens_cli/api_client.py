import httpx
import os
import keyring
from typing import Optional
import json

class TestLensAPIError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code

class AuthRequiredError(Exception):
    pass

class TestLensClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self._token: Optional[str] = None
        
    def _get_token(self) -> str:
        if self._token:
            return self._token
            
        # 1. Try env var first (CI override)
        token = os.environ.get("TESTLENS_API_TOKEN")
        if token:
            self._token = token
            return token
            
        # 2. Try OS Keyring
        try:
            token = keyring.get_password("testlens-cli", "auth-token")
        except Exception:
            token = None
            
        # 3. Try fallback config file (if keyring failed)
        if not token:
            config_path = os.path.expanduser("~/.testlens/config.json")
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r") as f:
                        cfg = json.load(f)
                        token = cfg.get("token")
                except Exception:
                    pass
                    
        if not token:
            raise AuthRequiredError("Not authenticated. Please run `testlens login` or set TESTLENS_API_TOKEN.")
            
        self._token = token
        return token

    def _request(self, method: str, path: str, **kwargs) -> dict:
        url = f"{self.base_url}/api/v1{path}"
        headers = kwargs.pop("headers", {})
        
        try:
            token = self._get_token()
            headers["Authorization"] = f"Bearer {token}"
        except AuthRequiredError:
            # Login endpoints don't need auth
            if not path.startswith("/auth/"):
                raise
                
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.request(method, url, headers=headers, **kwargs)
                
            if response.status_code == 401:
                raise AuthRequiredError("Session expired. Please run `testlens login`.")
                
            if not response.is_success:
                msg = f"API Error: {response.status_code} {response.reason_phrase}"
                try:
                    data = response.json()
                    msg = data.get("detail", msg)
                except Exception:
                    pass
                raise TestLensAPIError(msg, response.status_code)
                
            return response.json()
            
        except httpx.RequestError as e:
            raise TestLensAPIError(f"Network error connecting to {url}. Please check your connection or `testlens config show`.")

    def get_failures(self, repo_id: str, limit: int = 20, page: int = 1) -> dict:
        return self._request("GET", "/failures", params={"repository_id": repo_id, "limit": limit, "page": page})

    def analyze_failure(self, failure_id: str) -> dict:
        return self._request("POST", f"/failures/{failure_id}/analyze")
        
    def get_flaky_leaderboard(self, repo_id: str) -> list:
        return self._request("GET", "/analytics/leaderboard/flaky-tests", params={"repository_id": repo_id})
