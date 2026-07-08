import uuid
from datetime import datetime, timezone, timedelta
from jose import jwt
from services.auth.application.ports import UserRepositoryPort, OAuthProviderPort
from services.auth.domain.entities import User
from services.auth.domain.value_objects import Email, TokenPair
from shared.config import settings
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class LoginWithOAuthUseCase:
    def __init__(self, user_repo: UserRepositoryPort, oauth_provider: OAuthProviderPort):
        self.user_repo = user_repo
        self.oauth_provider = oauth_provider

    async def execute(self, code: str, ip: str = "0.0.0.0") -> TokenPair:
        user_info = await self.oauth_provider.exchange_code_for_user_info(code)
        email_str = user_info.get("email")
        full_name = user_info.get("name") or email_str
        
        if not email_str:
            raise ValueError("OAuth provider did not return an email")
            
        email = Email(address=email_str)
        user = await self.user_repo.get_by_email(email)
        
        if not user:
            user = User(
                id=str(uuid.uuid4()),
                email=email.address,
                full_name=full_name,
                hashed_password=None # No password for OAuth users initially
            )
            user = await self.user_repo.create(user)
            logger.info("New user registered via OAuth", extra={"user_id": user.id, "email": email.address})
        
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
        
        logger.info("Successful login via OAuth", extra={"user_id": user.id, "ip": ip})
        return TokenPair(access_token=access_token, refresh_token=refresh_token, expires_in=settings.access_token_ttl_seconds)
