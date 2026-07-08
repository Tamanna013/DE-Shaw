from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import json

@dataclass
class Notification:
    id: str
    user_id: str
    event_type: str
    event_id: str # The outbox event UUID for deduplication
    channel: str # 'in_app', 'email', 'slack'
    payload: Dict
    is_read: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class NotificationPreference:
    user_id: str
    preferences: Dict[str, List[str]] # e.g. {"failure.analyzed": ["in_app", "email"]}

class DomainEvent:
    def __init__(self, id: str, type: str, payload: dict):
        self.id = id
        self.type = type
        self.payload = payload

# Sensible Defaults
DEFAULT_PREFERENCES = {
    "failure.analyzed": ["in_app"],
    "test.flagged_flaky": ["in_app", "slack"],
    "digest.weekly_ready": ["in_app", "email"]
}

VALID_CHANNELS_PER_EVENT = {
    "failure.analyzed": ["in_app", "email", "slack"],
    "test.flagged_flaky": ["in_app", "slack"],
    "digest.weekly_ready": ["in_app", "email"]
}
