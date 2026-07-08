from pydantic import BaseModel
from typing import List, Optional

class WebhookPushEventSchema(BaseModel):
    ref: str
    before: str
    after: str
    commits: List[dict]
    repository: dict

class WebhookResponseSchema(BaseModel):
    status: str
    commits: Optional[int] = None
    reason: Optional[str] = None
