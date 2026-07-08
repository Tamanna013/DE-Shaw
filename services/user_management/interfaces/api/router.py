import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List

from services.user_management.interfaces.api.schemas import (
    UserProfileResponse, AssignRoleRequest, UpdateProfileRequest,
    CreateTeamRequest, TeamResponse, AddTeamMemberRequest, PaginatedUsersResponse
)
from services.user_management.application.use_cases.assign_role import AssignRoleUseCase
from services.user_management.application.use_cases.create_team import CreateTeamUseCase
from services.user_management.application.use_cases.add_user_to_team import AddUserToTeamUseCase
from services.user_management.application.use_cases.update_profile import UpdateProfileUseCase
from services.user_management.application.use_cases.deactivate_user import DeactivateUserUseCase
from services.user_management.application.ports import UserProfileRepositoryPort, TeamRepositoryPort
from services.user_management.infrastructure.db.repository import SQLAlchemyUserProfileRepository, SQLAlchemyTeamRepository
from services.user_management.domain.exceptions import UnauthorizedError, ResourceNotFoundError, LastAdminRemovalError, UserAlreadyInTeamError, TeamNotEmptyError

# Inter-module dependency
from services.auth.interfaces.api.dependencies import get_current_user, get_db_session
from services.auth.domain.entities import User as AuthUser
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1", tags=["user_management"])

def get_user_repo(session: AsyncSession = Depends(get_db_session)) -> UserProfileRepositoryPort:
    return SQLAlchemyUserProfileRepository(session)

def get_team_repo(session: AsyncSession = Depends(get_db_session)) -> TeamRepositoryPort:
    return SQLAlchemyTeamRepository(session)

def format_error(code: str, message: str) -> dict:
    return {"error": {"code": code, "message": message, "trace_id": str(uuid.uuid4())}}


@router.get("/users", response_model=PaginatedUsersResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[str] = None,
    team_id: Optional[str] = None,
    user_repo: UserProfileRepositoryPort = Depends(get_user_repo),
    current_user: AuthUser = Depends(get_current_user)
):
    users = await user_repo.list_users(page, page_size, role, team_id)
    return PaginatedUsersResponse(
        items=[UserProfileResponse(**u.__dict__) for u in users],
        page=page,
        page_size=page_size
    )

@router.get("/users/{user_id}", response_model=UserProfileResponse)
async def get_user(
    user_id: str,
    user_repo: UserProfileRepositoryPort = Depends(get_user_repo),
    current_user: AuthUser = Depends(get_current_user)
):
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=format_error("NOT_FOUND", "User not found"))
    return UserProfileResponse(**user.__dict__)

@router.patch("/users/{user_id}", response_model=UserProfileResponse)
async def update_user(
    user_id: str,
    req: UpdateProfileRequest,
    user_repo: UserProfileRepositoryPort = Depends(get_user_repo),
    current_user: AuthUser = Depends(get_current_user)
):
    use_case = UpdateProfileUseCase(user_repo)
    try:
        user = await use_case.execute(current_user.id, user_id, req.full_name, req.team_id)
        return UserProfileResponse(**user.__dict__)
    except UnauthorizedError as e:
        raise HTTPException(status_code=403, detail=format_error("UNAUTHORIZED", str(e)))
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=format_error("NOT_FOUND", str(e)))

@router.post("/users/{user_id}/role", response_model=UserProfileResponse)
async def assign_role(
    user_id: str,
    req: AssignRoleRequest,
    user_repo: UserProfileRepositoryPort = Depends(get_user_repo),
    current_user: AuthUser = Depends(get_current_user)
):
    use_case = AssignRoleUseCase(user_repo)
    try:
        user = await use_case.execute(current_user.id, user_id, req.role)
        return UserProfileResponse(**user.__dict__)
    except UnauthorizedError as e:
        raise HTTPException(status_code=403, detail=format_error("UNAUTHORIZED", str(e)))
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=format_error("NOT_FOUND", str(e)))
    except LastAdminRemovalError as e:
        raise HTTPException(status_code=400, detail=format_error("LAST_ADMIN", str(e)))

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: str,
    user_repo: UserProfileRepositoryPort = Depends(get_user_repo),
    current_user: AuthUser = Depends(get_current_user)
):
    use_case = DeactivateUserUseCase(user_repo)
    try:
        await use_case.execute(current_user.id, user_id)
        return None
    except UnauthorizedError as e:
        raise HTTPException(status_code=403, detail=format_error("UNAUTHORIZED", str(e)))
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=format_error("NOT_FOUND", str(e)))
    except LastAdminRemovalError as e:
        raise HTTPException(status_code=400, detail=format_error("LAST_ADMIN", str(e)))

@router.post("/teams", status_code=status.HTTP_201_CREATED, response_model=TeamResponse)
async def create_team(
    req: CreateTeamRequest,
    team_repo: TeamRepositoryPort = Depends(get_team_repo),
    user_repo: UserProfileRepositoryPort = Depends(get_user_repo),
    current_user: AuthUser = Depends(get_current_user)
):
    use_case = CreateTeamUseCase(team_repo, user_repo)
    try:
        team = await use_case.execute(current_user.id, req.name, req.description)
        return TeamResponse(**team.__dict__)
    except UnauthorizedError as e:
        raise HTTPException(status_code=403, detail=format_error("UNAUTHORIZED", str(e)))

@router.post("/teams/{team_id}/members", status_code=status.HTTP_204_NO_CONTENT)
async def add_team_member(
    team_id: str,
    req: AddTeamMemberRequest,
    team_repo: TeamRepositoryPort = Depends(get_team_repo),
    user_repo: UserProfileRepositoryPort = Depends(get_user_repo),
    current_user: AuthUser = Depends(get_current_user)
):
    use_case = AddUserToTeamUseCase(team_repo, user_repo)
    try:
        await use_case.execute(current_user.id, team_id, req.user_id)
        return None
    except UnauthorizedError as e:
        raise HTTPException(status_code=403, detail=format_error("UNAUTHORIZED", str(e)))
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=format_error("NOT_FOUND", str(e)))
    except UserAlreadyInTeamError as e:
        raise HTTPException(status_code=409, detail=format_error("ALREADY_IN_TEAM", str(e)))

@router.get("/teams/{team_id}/members", response_model=List[UserProfileResponse])
async def list_team_members(
    team_id: str,
    team_repo: TeamRepositoryPort = Depends(get_team_repo),
    current_user: AuthUser = Depends(get_current_user)
):
    members = await team_repo.list_members(team_id)
    return [UserProfileResponse(**m.__dict__) for m in members]

@router.delete("/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: str,
    force: bool = Query(False),
    team_repo: TeamRepositoryPort = Depends(get_team_repo),
    user_repo: UserProfileRepositoryPort = Depends(get_user_repo),
    current_user: AuthUser = Depends(get_current_user)
):
    actor = await user_repo.get_by_id(current_user.id)
    if not actor or actor.role not in (Role.ADMIN.value, Role.ENGINEERING_MANAGER.value):
        raise HTTPException(status_code=403, detail=format_error("UNAUTHORIZED", "Only Admins/Managers can delete teams."))
    
    count = await team_repo.get_member_count(team_id)
    if count > 0 and not force:
        raise HTTPException(status_code=409, detail=format_error("TEAM_NOT_EMPTY", f"Team has {count} active members. Use force=true to delete."))
        
    await team_repo.delete(team_id)
    return None
