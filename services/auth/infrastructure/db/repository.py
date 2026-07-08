from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from services.auth.application.ports import UserRepositoryPort
from services.auth.domain.entities import User, BlockedDomain
from services.auth.domain.value_objects import Email
from services.auth.domain.exceptions import DuplicateEmailError
from services.auth.infrastructure.db.models import UserModel, BlockedEmailDomainModel

class SQLAlchemyUserRepository(UserRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: str) -> Optional[User]:
        result = await self.session.execute(select(UserModel).where(UserModel.id == user_id))
        model = result.scalar_one_or_none()
        if model:
            return User(
                id=model.id,
                email=model.email,
                full_name=model.full_name,
                hashed_password=model.hashed_password,
                created_at=model.created_at,
                updated_at=model.updated_at
            )
        return None

    async def get_by_email(self, email: Email) -> Optional[User]:
        result = await self.session.execute(select(UserModel).where(UserModel.email == email.address))
        model = result.scalar_one_or_none()
        if model:
            return User(
                id=model.id,
                email=model.email,
                full_name=model.full_name,
                hashed_password=model.hashed_password,
                created_at=model.created_at,
                updated_at=model.updated_at
            )
        return None

    async def create(self, user: User) -> User:
        model = UserModel(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            hashed_password=user.hashed_password
        )
        self.session.add(model)
        try:
            await self.session.commit()
            await self.session.refresh(model)
            return User(
                id=model.id,
                email=model.email,
                full_name=model.full_name,
                hashed_password=model.hashed_password,
                created_at=model.created_at,
                updated_at=model.updated_at
            )
        except IntegrityError:
            await self.session.rollback()
            raise DuplicateEmailError(f"Email {user.email} is already registered")

    async def get_blocked_domain(self, domain: str) -> Optional[BlockedDomain]:
        result = await self.session.execute(select(BlockedEmailDomainModel).where(BlockedEmailDomainModel.domain == domain))
        model = result.scalar_one_or_none()
        if model:
            return BlockedDomain(domain=model.domain)
        return None
