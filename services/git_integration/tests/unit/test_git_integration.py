import pytest
import hmac
import hashlib
from unittest.mock import AsyncMock, patch
from services.git_integration.application.use_cases.register_repository_webhook import RegisterRepositoryWebhookUseCase
from services.git_integration.domain.exceptions import InvalidWebhookSignatureError, ProviderAPIError
from services.git_integration.domain.entities import RepositoryRef
from services.git_integration.application.use_cases.fetch_commit import FetchCommitUseCase
from services.git_integration.application.use_cases.fetch_diff_between_shas import FetchDiffBetweenShasUseCase

@pytest.fixture
def repo():
    return RepositoryRef(
        id="repo-1",
        owner="testlens",
        name="backend",
        provider="github",
        clone_url="git@github.com:testlens/backend.git",
        webhook_secret="super-secret"
    )

@pytest.fixture
def mock_queue():
    queue = AsyncMock()
    queue.enqueue_push_event = AsyncMock()
    return queue

@pytest.mark.asyncio
async def test_webhook_signature_verification_rejects_invalid_signature(repo, mock_queue):
    use_case = RegisterRepositoryWebhookUseCase(mock_queue)
    payload = b'{"commits": [{"id": "abc"}]}'
    
    # Generate bad sig
    bad_sig = "sha256=abcdef123456"
    
    with pytest.raises(InvalidWebhookSignatureError):
        await use_case.execute(repo, bad_sig, payload, ["abc"], "refs/heads/main")
        
    # Generate valid sig
    valid_mac = hmac.new("super-secret".encode(), payload, hashlib.sha256).hexdigest()
    valid_sig = f"sha256={valid_mac}"
    
    result = await use_case.execute(repo, valid_sig, payload, ["abc"], "refs/heads/main")
    assert result["status"] == "enqueued"
    mock_queue.enqueue_push_event.assert_called_once()

@pytest.mark.asyncio
async def test_rate_limit_awareness_switches_to_local_mirror_below_threshold(repo):
    mock_provider = AsyncMock()
    mock_provider.get_rate_limit_remaining.return_value = 50 # Below 100 threshold
    
    mock_mirror = AsyncMock()
    
    use_case = FetchCommitUseCase(mock_provider, mock_mirror)
    await use_case.execute(repo, "abc")
    
    # Provider fetch should NOT be called
    mock_provider.fetch_commit.assert_not_called()
    
    # Mirror ensure and fetch SHOULD be called
    mock_mirror.ensure_cloned.assert_called_once()
    mock_mirror.fetch_commit.assert_called_once()

@pytest.mark.asyncio
async def test_force_push_orphaned_commit_handling(repo):
    mock_provider = AsyncMock()
    mock_provider.get_rate_limit_remaining.return_value = 5000
    mock_provider.fetch_commit.side_effect = ProviderAPIError("Not Found", status_code=404)
    
    mock_mirror = AsyncMock()
    
    use_case = FetchCommitUseCase(mock_provider, mock_mirror)
    
    # Even if API says 404, we fallback to mirror in case it's a known orphaned commit locally
    await use_case.execute(repo, "abc")
    
    mock_mirror.ensure_cloned.assert_called_once()
    mock_mirror.fetch_commit.assert_called_once()

@pytest.mark.asyncio
async def test_large_diff_pagination(repo):
    mock_provider = AsyncMock()
    mock_provider.get_rate_limit_remaining.return_value = 5000
    
    # Simulate paginated diff
    mock_provider.fetch_diff.side_effect = [
        [{"file_path": f"file_{i}"} for i in range(100)], # Page 1
        [{"file_path": f"file_{i}"} for i in range(100, 150)], # Page 2 (partial)
    ]
    
    mock_mirror = AsyncMock()
    
    use_case = FetchDiffBetweenShasUseCase(mock_provider, mock_mirror)
    diffs = await use_case.execute(repo, "base", "head")
    
    assert len(diffs) == 150
    assert mock_provider.fetch_diff.call_count == 2
