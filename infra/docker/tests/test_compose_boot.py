import subprocess
import time
import requests
import pytest

def run_cmd(cmd: str):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

@pytest.fixture(scope="module")
def compose_stack():
    """Spins up the full compose stack and tears it down after tests."""
    print("Starting full compose stack. This may take a minute...")
    run_cmd("docker-compose -f infra/docker/docker-compose.yml up -d")
    
    # Wait for the API gateway healthcheck to pass
    # Since gateway depends on DB and Redis (with service_healthy condition),
    # this implies the backing stores are also up.
    gateway_url = "http://localhost:8000/healthz"
    max_retries = 30
    ready = False
    
    for _ in range(max_retries):
        try:
            resp = requests.get(gateway_url, timeout=2)
            if resp.status_code == 200:
                ready = True
                break
        except requests.RequestException:
            pass
        time.sleep(2)
        
    if not ready:
        run_cmd("docker-compose -f infra/docker/docker-compose.yml logs")
        run_cmd("docker-compose -f infra/docker/docker-compose.yml down -v")
        pytest.fail("Compose stack failed to become ready within timeout.")
        
    yield
    
    print("Tearing down compose stack...")
    run_cmd("docker-compose -f infra/docker/docker-compose.yml down -v")

def test_full_stack_boot(compose_stack):
    """
    Smoke test checking the gateway's readiness probe.
    The readiness probe checks DB and Redis connectivity.
    """
    resp = requests.get("http://localhost:8000/readyz", timeout=5)
    assert resp.status_code == 200
    
    data = resp.json()
    assert data["status"] == "ok"
    assert data["dependencies"]["db"] == "ok"
    assert data["dependencies"]["redis"] == "ok"
