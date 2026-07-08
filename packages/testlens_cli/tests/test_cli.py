import pytest
import json
import sys
from typer.testing import CliRunner
from testlens_cli.main import app

runner = CliRunner()

@pytest.fixture
def mock_auth(monkeypatch):
    monkeypatch.setenv("TESTLENS_API_TOKEN", "mock-token")

def test_missing_repo_fails_with_clear_message(monkeypatch, mock_auth):
    # Mock no default repo in config
    monkeypatch.setattr("testlens_cli.commands.config._get_default_repo", lambda: None)
    
    result = runner.invoke(app, ["failures", "list"])
    
    assert result.exit_code == 1
    assert "No repository specified" in result.stdout
    assert "testlens config set-repo" in result.stdout

def test_json_output_is_valid_json(monkeypatch, mock_auth):
    monkeypatch.setattr("testlens_cli.commands.config._get_default_repo", lambda: "mock-repo")
    
    # Mock the API client
    class MockClient:
        def get_failures(self, *args, **kwargs):
            return {"items": [{"id": "1", "test_name": "test_foo"}]}
            
    monkeypatch.setattr("testlens_cli.commands.failures.TestLensClient", MockClient)
    
    # Simulate --json passed to argv
    monkeypatch.setattr(sys, "argv", ["testlens", "failures", "list", "--json"])
    
    result = runner.invoke(app, ["failures", "list", "--json"])
    
    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert "items" in parsed
    assert parsed["items"][0]["test_name"] == "test_foo"

def test_auth_error_returns_exit_code_2(monkeypatch):
    # No keyring, no env var, no config file
    monkeypatch.setattr("keyring.get_password", lambda *args: None)
    monkeypatch.delenv("TESTLENS_API_TOKEN", raising=False)
    monkeypatch.setattr("os.path.exists", lambda path: False)
    
    monkeypatch.setattr("testlens_cli.commands.config._get_default_repo", lambda: "mock-repo")
    
    result = runner.invoke(app, ["failures", "list"])
    
    # Auth Required error handled gracefully
    assert result.exit_code == 2
    assert "Not authenticated" in result.stdout
