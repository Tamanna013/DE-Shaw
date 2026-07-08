from pydantic import BaseModel
from typing import Dict, List

class NotificationSchema(BaseModel):
    id: str
    event_type: str
    channel: str
    payload: dict
    is_read: bool
    created_at: str

class UpdatePreferencesRequest(BaseModel):
    preferences: Dict[str, List[str]]
