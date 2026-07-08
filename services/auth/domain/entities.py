from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class User:
    id: str
    email: str
    full_name: str
    hashed_password: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Session:
    user_id: str
    refresh_token_jti: str
    expires_at: datetime
    revoked: bool = False

@dataclass
class BlockedDomain:
    domain: str
