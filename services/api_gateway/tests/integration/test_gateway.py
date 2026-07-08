import pytest
from fastapi.testclient import TestClient
from services.api_gateway.main import app

client = TestClient(app)

def test_healthz_always_200():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_readyz_503_when_db_unreachable(monkeypatch):
    # Mock check_db to fail
    import services.api_gateway.health as health_module
    
    async def mock_check_db():
        return False
        
    monkeypatch.setattr(health_module, "check_db", mock_check_db)
    
    response = client.get("/readyz")
    assert response.status_code == 503
    
    data = response.json()
    assert data["status"] == "error"
    assert data["dependencies"]["db"] == "unreachable"

def test_request_id_injected_in_headers():
    response = client.get("/healthz")
    assert "X-Request-Id" in response.headers
    assert len(response.headers["X-Request-Id"]) > 0

@pytest.mark.parametrize("is_auth, max_requests", [
    (False, 100),
    (True, 1000)
])
def test_rate_limit_enforced_per_tier(is_auth, max_requests, monkeypatch):
    # Reset singleton limiter state
    import services.api_gateway.middleware.rate_limit as rl
    rl.limiter.anonymous_buckets.clear()
    rl.auth_buckets = {}
    
    headers = {"Authorization": "Bearer testuser123"} if is_auth else {}
    
    # Exhaust the bucket
    for _ in range(max_requests):
        resp = client.get("/healthz", headers=headers)
        assert resp.status_code == 200
        
    # Next request should 429
    resp = client.get("/healthz", headers=headers)
    assert resp.status_code == 429
    assert resp.text == "Too Many Requests"

def test_cors_rejects_non_allowlisted_origin():
    # client sends a different origin
    headers = {
        "Origin": "http://evil.com",
        "Access-Control-Request-Method": "GET"
    }
    # Preflight request
    response = client.options("/healthz", headers=headers)
    
    # FastAPI's CORSMiddleware returns 400 for bad origins in preflight
    assert response.status_code == 400
    assert "Disallowed CORS origin" in response.text
