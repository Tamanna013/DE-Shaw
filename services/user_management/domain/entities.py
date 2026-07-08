from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class UserProfile:
    id: str
    email: str
    full_name: str
    role: str
    team_id: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Team:
    id: str
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
