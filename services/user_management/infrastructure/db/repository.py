from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from services.user_management.application.ports import UserProfileRepositoryPort, TeamRepositoryPort
from services.user_management.domain.entities import UserProfile, Team
from services.user_management.domain.roles import Role
from services.user_management.infrastructure.db.models import UserProfileModel, TeamModel, team_members

class SQLAlchemyUserProfileRepository(UserProfileRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: str) -> Optional[UserProfile]:
        result = await self.session.execute(select(UserProfileModel).where(UserProfileModel.id == user_id))
        model = result.scalar_one_or_none()
        if model:
            return self._to_entity(model)
        return None

    async def get_by_email(self, email: str) -> Optional[UserProfile]:
        result = await self.session.execute(select(UserProfileModel).where(UserProfileModel.email == email))
        model = result.scalar_one_or_none()
        if model:
            return self._to_entity(model)
        return None

    async def create(self, profile: UserProfile) -> UserProfile:
        model = UserProfileModel(
            id=profile.id,
            email=profile.email,
            full_name=profile.full_name,
            role=profile.role,
            team_id=profile.team_id,
            is_active=profile.is_active
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def update(self, profile: UserProfile) -> UserProfile:
        result = await self.session.execute(select(UserProfileModel).where(UserProfileModel.id == profile.id))
        model = result.scalar_one()
        model.full_name = profile.full_name
        model.role = profile.role
        model.team_id = profile.team_id
        model.is_active = profile.is_active
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def count_users_by_role(self, role: Role) -> int:
        result = await self.session.execute(select(func.count()).select_from(UserProfileModel).where(UserProfileModel.role == role.value, UserProfileModel.is_active == True))
        return result.scalar_one()

    async def list_users(self, page: int, page_size: int, role: Optional[str] = None, team_id: Optional[str] = None) -> list[UserProfile]:
        query = select(UserProfileModel)
        if role:
            query = query.where(UserProfileModel.role == role)
        if team_id:
            query = query.where(UserProfileModel.team_id == team_id)
            
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    def _to_entity(self, model: UserProfileModel) -> UserProfile:
        return UserProfile(
            id=model.id,
            email=model.email,
            full_name=model.full_name,
            role=model.role,
            team_id=model.team_id,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )


class SQLAlchemyTeamRepository(TeamRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, team_id: str) -> Optional[Team]:
        result = await self.session.execute(select(TeamModel).where(TeamModel.id == team_id))
        model = result.scalar_one_or_none()
        if model:
            return Team(
                id=model.id,
                name=model.name,
                description=model.description,
                created_at=model.created_at,
                updated_at=model.updated_at
            )
        return None

    async def create(self, team: Team) -> Team:
        model = TeamModel(
            id=team.id,
            name=team.name,
            description=team.description
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return Team(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    async def delete(self, team_id: str) -> None:
        result = await self.session.execute(select(TeamModel).where(TeamModel.id == team_id))
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.commit()

    async def get_member_count(self, team_id: str) -> int:
        result = await self.session.execute(select(func.count()).select_from(team_members).where(team_members.c.team_id == team_id))
        return result.scalar_one()

    async def add_member(self, team_id: str, user_id: str) -> None:
        stmt = team_members.insert().values(team_id=team_id, user_id=user_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def remove_member(self, team_id: str, user_id: str) -> None:
        stmt = team_members.delete().where(team_members.c.team_id == team_id, team_members.c.user_id == user_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def is_member(self, team_id: str, user_id: str) -> bool:
        result = await self.session.execute(select(1).select_from(team_members).where(team_members.c.team_id == team_id, team_members.c.user_id == user_id))
        return result.scalar_one_or_none() is not None

    async def list_members(self, team_id: str) -> list[UserProfile]:
        query = select(UserProfileModel).join(team_members).where(team_members.c.team_id == team_id)
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [
            UserProfile(
                id=m.id, email=m.email, full_name=m.full_name, role=m.role,
                team_id=m.team_id, is_active=m.is_active, created_at=m.created_at, updated_at=m.updated_at
            ) for m in models
        ]
