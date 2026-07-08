import pytest
from fastapi.testclient import TestClient
from services.api_gateway.main import app

client = TestClient(app)

@pytest.mark.parametrize("error_type, expected_status, expected_code", [
    ("auth", 401, "UNAUTHORIZED"),
    ("authz", 403, "FORBIDDEN"),
    ("notfound", 404, "NOT_FOUND"),
    ("conflict", 409, "CONFLICT"),
    ("validation", 422, "VALIDATION_ERROR"),
    ("internal", 500, "INTERNAL_SERVER_ERROR") # Tests that raw ValueErrors don't leak
])
def test_every_domain_exception_type_maps_to_documented_status_code(error_type, expected_status, expected_code):
    response = client.get(f"/api/v1/trigger-error?type={error_type}")
    
    assert response.status_code == expected_status
    data = response.json()
    
    assert "error" in data
    assert data["error"]["code"] == expected_code
    
    # Ensure trace_id is attached to every error
    assert "trace_id" in data["error"]
    
    if expected_status == 500:
        # Crucial security check: the raw error message ("Something unexpected broke") MUST NOT leak to the client
        assert "unexpected broke" not in data["error"]["message"]
        assert "unexpected error occurred" in data["error"]["message"]
