from fastapi import APIRouter, HTTPException, Depends, Header, Request
from typing import Optional
from services.git_integration.interfaces.api.schemas import WebhookResponseSchema
from services.git_integration.domain.entities import RepositoryRef
from services.git_integration.domain.exceptions import InvalidWebhookSignatureError
from services.git_integration.application.use_cases.register_repository_webhook import RegisterRepositoryWebhookUseCase
from services.git_integration.application.ports import WebhookTaskQueuePort
from shared.logging_engine import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/repos", tags=["git_integration"])

# Mock Task Queue
class MockTaskQueue(WebhookTaskQueuePort):
    async def enqueue_push_event(self, repo_id: str, shas: list, ref: str) -> None:
        pass

queue_port = MockTaskQueue()
register_webhook_use_case = RegisterRepositoryWebhookUseCase(queue_port)

@router.post("/{repo_id}/webhook", response_model=WebhookResponseSchema)
async def handle_webhook(
    repo_id: str,
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None)
):
    """
    Handles incoming GitHub webhooks for push events.
    Verifies HMAC and enqueues sync tasks quickly.
    """
    payload_bytes = await request.body()
    payload_json = await request.json()
    
    # In reality, fetch this from the database based on repo_id
    mock_repo = RepositoryRef(
        id=repo_id,
        owner=payload_json.get("repository", {}).get("owner", {}).get("name", "owner"),
        name=payload_json.get("repository", {}).get("name", "name"),
        provider="github",
        clone_url="",
        webhook_secret="test_secret" # Mock secret for testing
    )
    
    # If there is no signature header, but we expect one, fail
    if not x_hub_signature_256:
        raise HTTPException(status_code=401, detail="Missing webhook signature")

    shas = [c.get("id") for c in payload_json.get("commits", [])]
    ref = payload_json.get("ref", "refs/heads/main")
    
    try:
        result = await register_webhook_use_case.execute(
            mock_repo,
            x_hub_signature_256,
            payload_bytes,
            shas,
            ref
        )
        return WebhookResponseSchema(**result)
    except InvalidWebhookSignatureError:
        raise HTTPException(status_code=401, detail="Invalid HMAC signature")
