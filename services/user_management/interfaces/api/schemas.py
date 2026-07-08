from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from services.user_management.domain.roles import Role

class UserProfileResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: str
    team_id: Optional[str]
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class AssignRoleRequest(BaseModel):
    role: Role

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    team_id: Optional[str] = None

class CreateTeamRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None

class TeamResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class AddTeamMemberRequest(BaseModel):
    user_id: str

class PaginatedUsersResponse(BaseModel):
    items: List[UserProfileResponse]
    page: int
    page_size: int
