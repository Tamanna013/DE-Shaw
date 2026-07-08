import uuid
from datetime import datetime, timezone, timedelta
from typing import Tuple
from jose import jwt
from passlib.context import CryptContext
from services.auth.application.ports import UserRepositoryPort, TokenStorePort
from services.auth.domain.value_objects import Email, TokenPair
from services.auth.domain.exceptions import InvalidCredentialsError, RateLimitExceededError
from shared.config import settings
from shared.logging_engine import get_logger

logger = get_logger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginWithPasswordUseCase:
    def __init__(self, user_repo: UserRepositoryPort, token_store: TokenStorePort):
        self.user_repo = user_repo
        self.token_store = token_store

    async def execute(self, email_str: str, password: str, ip: str = "0.0.0.0") -> TokenPair:
        email = Email(address=email_str)
        attempts = await self.token_store.get_failed_logins(email)
        if attempts >= 5:
            logger.warning("Rate limit triggered for login", extra={"email": email_str, "ip": ip})
            raise RateLimitExceededError(retry_after=900)

        user = await self.user_repo.get_by_email(email)
        if not user or not user.hashed_password or not pwd_context.verify(password, user.hashed_password):
            await self.token_store.record_failed_login(email)
            logger.warning("Failed login attempt", extra={"email": email_str, "ip": ip})
            raise InvalidCredentialsError("Invalid email or password")

        await self.token_store.clear_failed_logins(email)
        
        now = datetime.now(timezone.utc)
        jti = str(uuid.uuid4())
        
        access_payload = {
            "sub": user.id,
            "type": "access",
            "exp": now + timedelta(seconds=settings.access_token_ttl_seconds),
            "nbf": now
        }
        
        refresh_payload = {
            "sub": user.id,
            "jti": jti,
            "type": "refresh",
            "exp": now + timedelta(seconds=settings.refresh_token_ttl_seconds),
            "nbf": now
        }
        
        access_token = jwt.encode(access_payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        refresh_token = jwt.encode(refresh_payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        
        logger.info("Successful login", extra={"user_id": user.id, "ip": ip})
        return TokenPair(access_token=access_token, refresh_token=refresh_token, expires_in=settings.access_token_ttl_seconds)
