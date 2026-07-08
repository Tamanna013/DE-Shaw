import uuid
from passlib.context import CryptContext
from services.auth.application.ports import UserRepositoryPort
from services.auth.domain.entities import User
from services.auth.domain.value_objects import Email
from services.auth.domain.exceptions import DomainError
from shared.logging_engine import get_logger

logger = get_logger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class RegisterUserUseCase:
    def __init__(self, user_repo: UserRepositoryPort):
        self.user_repo = user_repo

    async def execute(self, email_str: str, password: str, full_name: str) -> User:
        email = Email(address=email_str)
        domain = email_str.split("@")[-1]
        
        blocked = await self.user_repo.get_blocked_domain(domain)
        if blocked:
            logger.warning("Attempted registration with blocked domain", extra={"email": email_str})
            raise DomainError(f"Email domain {domain} is blocked")

        hashed_pwd = pwd_context.hash(password)
        
        user = User(
            id=str(uuid.uuid4()),
            email=email.address,
            full_name=full_name,
            hashed_password=hashed_pwd
        )
        
        created_user = await self.user_repo.create(user)
        logger.info("User registered successfully", extra={"user_id": created_user.id})
        return created_user
