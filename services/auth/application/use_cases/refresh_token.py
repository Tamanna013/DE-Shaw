import uuid
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
from services.auth.application.ports import UserRepositoryPort, TokenStorePort
from services.auth.domain.value_objects import TokenPair
from services.auth.domain.exceptions import InvalidTokenError
from shared.config import settings
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class RefreshTokenUseCase:
    def __init__(self, user_repo: UserRepositoryPort, token_store: TokenStorePort):
        self.user_repo = user_repo
        self.token_store = token_store

    async def execute(self, refresh_token: str, ip: str = "0.0.0.0") -> TokenPair:
        try:
            payload = jwt.decode(refresh_token, settings.jwt_secret, algorithms=[settings.jwt_algorithm], leeway=30)
        except JWTError as e:
            raise InvalidTokenError(f"Invalid refresh token: {str(e)}")

        if payload.get("type") != "refresh":
            raise InvalidTokenError("Not a refresh token")

        jti = payload.get("jti")
        sub = payload.get("sub")
        if not jti or not sub:
            raise InvalidTokenError("Missing jti or sub in token")

        is_blocked = await self.token_store.is_refresh_token_blocked(jti)
        if is_blocked:
            # Token reuse detected! Ideally revoke entire session family.
            logger.warning("Refresh token reuse detected", extra={"user_id": sub, "jti": jti, "ip": ip})
            raise InvalidTokenError("Token has been revoked")

        user = await self.user_repo.get_by_id(sub)
        if not user:
            raise InvalidTokenError("User no longer exists")

        # Block the old refresh token
        exp = payload.get("exp", 0)
        now_ts = int(datetime.now(timezone.utc).timestamp())
        ttl = max(0, exp - now_ts)
        if ttl > 0:
            await self.token_store.block_refresh_token(jti, ttl)

        now = datetime.now(timezone.utc)
        new_jti = str(uuid.uuid4())
        
        access_payload = {
            "sub": user.id,
            "type": "access",
            "exp": now + timedelta(seconds=settings.access_token_ttl_seconds),
            "nbf": now
        }
        
        refresh_payload = {
            "sub": user.id,
            "jti": new_jti,
            "type": "refresh",
            "exp": now + timedelta(seconds=settings.refresh_token_ttl_seconds),
            "nbf": now
        }
        
        new_access = jwt.encode(access_payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        new_refresh = jwt.encode(refresh_payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        
        logger.info("Successful token refresh", extra={"user_id": user.id, "ip": ip})
        return TokenPair(access_token=new_access, refresh_token=new_refresh, expires_in=settings.access_token_ttl_seconds)
