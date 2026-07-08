from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from shared.config import settings
from services.auth.infrastructure.db.database import get_db_session
from services.auth.infrastructure.db.repository import SQLAlchemyUserRepository
from services.auth.infrastructure.redis_token_store import RedisTokenStore
from services.auth.application.use_cases.verify_token import VerifyTokenUseCase
from services.auth.application.ports import UserRepositoryPort, TokenStorePort
from services.auth.domain.entities import User
from services.auth.domain.exceptions import InvalidTokenError, TokenExpiredError

security = HTTPBearer()

async def get_redis_client() -> redis.Redis: # type: ignore
    return await redis.from_url(settings.redis_url) # type: ignore

async def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> UserRepositoryPort:
    return SQLAlchemyUserRepository(session)

async def get_token_store(redis_client: redis.Redis = Depends(get_redis_client)) -> TokenStorePort: # type: ignore
    return RedisTokenStore(redis_client)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_repo: UserRepositoryPort = Depends(get_user_repository)
) -> User:
    token = credentials.credentials
    verify_use_case = VerifyTokenUseCase()
    try:
        payload = await verify_use_case.execute(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
    except (InvalidTokenError, TokenExpiredError) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
