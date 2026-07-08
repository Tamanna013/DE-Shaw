from services.user_management.application.ports import UserProfileRepositoryPort
from services.user_management.domain.entities import UserProfile
from services.user_management.domain.roles import Role
from services.user_management.domain.exceptions import UnauthorizedError, ResourceNotFoundError, LastAdminRemovalError
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class AssignRoleUseCase:
    def __init__(self, repo: UserProfileRepositoryPort):
        self.repo = repo

    async def execute(self, admin_id: str, target_user_id: str, new_role: Role) -> UserProfile:
        admin_profile = await self.repo.get_by_id(admin_id)
        if not admin_profile or admin_profile.role != Role.ADMIN.value:
            raise UnauthorizedError("Only Admins can assign roles.")

        target_profile = await self.repo.get_by_id(target_user_id)
        if not target_profile:
            raise ResourceNotFoundError("User not found.")

        if target_profile.role == Role.ADMIN.value and new_role != Role.ADMIN:
            admin_count = await self.repo.count_users_by_role(Role.ADMIN)
            if admin_count <= 1:
                raise LastAdminRemovalError()

        old_role = target_profile.role
        target_profile.role = new_role.value
        updated_profile = await self.repo.update(target_profile)
        
        logger.info("Role assigned", extra={"actor_id": admin_id, "target_id": target_user_id, "old_role": old_role, "new_role": new_role.value})
        return updated_profile
