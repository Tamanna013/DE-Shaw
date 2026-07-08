from typing import Optional
from services.user_management.application.ports import UserProfileRepositoryPort
from services.user_management.domain.entities import UserProfile
from services.user_management.domain.roles import Role
from services.user_management.domain.exceptions import UnauthorizedError, ResourceNotFoundError

class UpdateProfileUseCase:
    def __init__(self, repo: UserProfileRepositoryPort):
        self.repo = repo

    async def execute(self, actor_id: str, target_user_id: str, full_name: Optional[str] = None, team_id: Optional[str] = None) -> UserProfile:
        if actor_id != target_user_id:
            actor_profile = await self.repo.get_by_id(actor_id)
            if not actor_profile or actor_profile.role != Role.ADMIN.value:
                raise UnauthorizedError("You can only update your own profile unless you are an Admin.")

        target_profile = await self.repo.get_by_id(target_user_id)
        if not target_profile:
            raise ResourceNotFoundError("User not found.")

        if full_name:
            target_profile.full_name = full_name
        if team_id is not None:
            target_profile.team_id = team_id

        return await self.repo.update(target_profile)
