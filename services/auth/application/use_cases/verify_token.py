from jose import jwt, JWTError
from services.auth.domain.exceptions import InvalidTokenError, TokenExpiredError
from shared.config import settings

class VerifyTokenUseCase:
    async def execute(self, token: str) -> dict[str, str]:
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm], leeway=30)
            if payload.get("type") != "access":
                raise InvalidTokenError("Not an access token")
            return payload # type: ignore
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token has expired")
        except JWTError as e:
            raise InvalidTokenError(f"Invalid token: {str(e)}")
