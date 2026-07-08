from services.user_management.application.ports import UserProfileRepositoryPort
from services.user_management.domain.roles import Role
from services.user_management.domain.exceptions import UnauthorizedError, ResourceNotFoundError, LastAdminRemovalError
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class DeactivateUserUseCase:
    def __init__(self, repo: UserProfileRepositoryPort):
        self.repo = repo

    async def execute(self, actor_id: str, target_user_id: str) -> None:
        actor_profile = await self.repo.get_by_id(actor_id)
        if not actor_profile or actor_profile.role != Role.ADMIN.value:
            raise UnauthorizedError("Only Admins can deactivate users.")

        target_profile = await self.repo.get_by_id(target_user_id)
        if not target_profile:
            raise ResourceNotFoundError("User not found.")

        if target_profile.role == Role.ADMIN.value:
            admin_count = await self.repo.count_users_by_role(Role.ADMIN)
            if admin_count <= 1:
                raise LastAdminRemovalError()

        target_profile.is_active = False
        await self.repo.update(target_profile)
        logger.info("User deactivated", extra={"actor_id": actor_id, "target_id": target_user_id})
