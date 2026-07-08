import uuid
from typing import Optional
from services.user_management.application.ports import TeamRepositoryPort, UserProfileRepositoryPort
from services.user_management.domain.entities import Team
from services.user_management.domain.roles import Role
from services.user_management.domain.exceptions import UnauthorizedError

class CreateTeamUseCase:
    def __init__(self, team_repo: TeamRepositoryPort, user_repo: UserProfileRepositoryPort):
        self.team_repo = team_repo
        self.user_repo = user_repo

    async def execute(self, creator_id: str, name: str, description: Optional[str] = None) -> Team:
        creator_profile = await self.user_repo.get_by_id(creator_id)
        if not creator_profile or creator_profile.role not in (Role.ADMIN.value, Role.ENGINEERING_MANAGER.value):
            raise UnauthorizedError("Only Admins or Engineering Managers can create teams.")

        team = Team(
            id=str(uuid.uuid4()),
            name=name,
            description=description
        )
        return await self.team_repo.create(team)
