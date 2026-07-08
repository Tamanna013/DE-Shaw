import subprocess
import pytest
import os

def run_script(script: str, args: list, env: dict = None):
    cmd = [script] + args
    
    # We must ensure the script is executable
    os.chmod(script, 0o755)
    
    env_vars = os.environ.copy()
    if env:
        env_vars.update(env)
        
    return subprocess.run(
        cmd,
        env=env_vars,
        capture_output=True,
        text=True
    )

def test_deploy_fails_if_env_file_missing():
    result = run_script("./deploy.sh", ["v1.0.0", "nonexistent"])
    assert result.returncode == 1
    assert "Environment file environments/nonexistent.env does not exist" in result.stdout

def test_deploy_happy_path(monkeypatch):
    # Mock curl to succeed instantly
    monkeypatch.setenv("PATH", f"/tmp/mock:{os.environ['PATH']}")
    os.makedirs("/tmp/mock", exist_ok=True)
    with open("/tmp/mock/curl", "w") as f:
        f.write("#!/bin/sh\nexit 0")
    os.chmod("/tmp/mock/curl", 0o755)
    
    result = run_script("./deploy.sh", ["v1.0.0", "dev"])
    assert result.returncode == 0
    assert "Deployment of v1.0.0 to dev completed successfully" in result.stdout

def test_deploy_triggers_rollback_on_health_failure(monkeypatch):
    # Mock curl to fail continuously
    monkeypatch.setenv("PATH", f"/tmp/mock_fail:{os.environ['PATH']}")
    os.makedirs("/tmp/mock_fail", exist_ok=True)
    with open("/tmp/mock_fail/curl", "w") as f:
        f.write("#!/bin/sh\nexit 1")
    os.chmod("/tmp/mock_fail/curl", 0o755)
    
    # Mock rollback.sh so it doesn't actually try to run docker commands
    with open("./rollback.sh", "w") as f:
        f.write("#!/bin/sh\necho 'MOCK ROLLBACK EXECUTED'")
    os.chmod("./rollback.sh", 0o755)
    
    # Reduce timeout for test speed (we can pass it via env or just patch the script)
    # For artifact simplicity we just run it and let it fail
    
    # Wait, the script has a 60s sleep loop. We should sed the script for the test.
    subprocess.run(["sed", "-i", "s/TIMEOUT=60/TIMEOUT=2/g", "./deploy.sh"])
    
    result = run_script("./deploy.sh", ["v1.0.0", "dev"])
    
    assert result.returncode == 1
    assert "Initiating automatic rollback" in result.stdout
    assert "MOCK ROLLBACK EXECUTED" in result.stdout
    
    # Restore script
    subprocess.run(["git", "checkout", "./deploy.sh"])
