from services.user_management.application.ports import TeamRepositoryPort, UserProfileRepositoryPort
from services.user_management.domain.roles import Role
from services.user_management.domain.exceptions import UnauthorizedError, ResourceNotFoundError, UserAlreadyInTeamError
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class AddUserToTeamUseCase:
    def __init__(self, team_repo: TeamRepositoryPort, user_repo: UserProfileRepositoryPort):
        self.team_repo = team_repo
        self.user_repo = user_repo

    async def execute(self, actor_id: str, team_id: str, user_id: str) -> None:
        actor_profile = await self.user_repo.get_by_id(actor_id)
        if not actor_profile or actor_profile.role not in (Role.ADMIN.value, Role.ENGINEERING_MANAGER.value):
            raise UnauthorizedError("Only Admins or Engineering Managers can manage teams.")

        team = await self.team_repo.get_by_id(team_id)
        if not team:
            raise ResourceNotFoundError("Team not found.")

        target_profile = await self.user_repo.get_by_id(user_id)
        if not target_profile:
            raise ResourceNotFoundError("User not found.")

        is_member = await self.team_repo.is_member(team_id, user_id)
        if is_member:
            raise UserAlreadyInTeamError(f"User {user_id} is already in team {team_id}.")

        await self.team_repo.add_member(team_id, user_id)
        logger.info("User added to team", extra={"actor_id": actor_id, "target_id": user_id, "team_id": team_id})
