import hmac
import hashlib
from typing import List, Optional
from services.git_integration.domain.entities import RepositoryRef
from services.git_integration.domain.exceptions import InvalidWebhookSignatureError
from services.git_integration.application.ports import WebhookTaskQueuePort
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class RegisterRepositoryWebhookUseCase:
    def __init__(self, task_queue: WebhookTaskQueuePort):
        self.task_queue = task_queue

    async def execute(self, repo: RepositoryRef, signature_header: str, payload_bytes: bytes, shas: List[str], ref: str) -> dict:
        # 1. Verify HMAC Signature
        if repo.webhook_secret:
            expected_mac = hmac.new(
                repo.webhook_secret.encode('utf-8'),
                payload_bytes,
                hashlib.sha256
            ).hexdigest()
            
            # GitHub sends 'sha256=...'
            expected_sig = f"sha256={expected_mac}"
            
            if not hmac.compare_digest(expected_sig, signature_header):
                logger.warning("Webhook signature verification failed (possible spoofing)", repo_id=repo.id)
                raise InvalidWebhookSignatureError("Invalid HMAC signature")
        
        # 2. Enqueue background sync (fast return < 2s for webhook requirements)
        if shas:
            await self.task_queue.enqueue_push_event(repo.id, shas, ref)
            logger.info("Webhook processed, sync enqueued", repo_id=repo.id, shas_count=len(shas))
            return {"status": "enqueued", "commits": len(shas)}
            
        return {"status": "ignored", "reason": "no_commits"}
