from services.user_management.application.ports import UserProfileRepositoryPort
from services.user_management.domain.entities import UserProfile
from services.user_management.domain.roles import Role

class CreateUserProfileUseCase:
    def __init__(self, repo: UserProfileRepositoryPort):
        self.repo = repo

    async def execute(self, user_id: str, email: str, full_name: str, role: Role = Role.DEVELOPER) -> UserProfile:
        existing = await self.repo.get_by_id(user_id)
        if existing:
            return existing

        profile = UserProfile(
            id=user_id,
            email=email,
            full_name=full_name,
            role=role.value
        )
        return await self.repo.create(profile)
