from datetime import datetime, timezone
from jose import jwt, JWTError
from services.auth.application.ports import TokenStorePort
from shared.config import settings
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class RevokeSessionUseCase:
    def __init__(self, token_store: TokenStorePort):
        self.token_store = token_store

    async def execute(self, refresh_token: str) -> None:
        try:
            payload = jwt.decode(refresh_token, settings.jwt_secret, algorithms=[settings.jwt_algorithm], options={"verify_exp": False})
        except JWTError:
            return # Ignore if already malformed

        jti = payload.get("jti")
        sub = payload.get("sub")
        exp = payload.get("exp", 0)
        
        if not jti:
            return
            
        now_ts = int(datetime.now(timezone.utc).timestamp())
        ttl = max(0, exp - now_ts)
        
        if ttl > 0:
            await self.token_store.block_refresh_token(jti, ttl)
            logger.info("Session revoked (logout)", extra={"user_id": sub, "jti": jti})
