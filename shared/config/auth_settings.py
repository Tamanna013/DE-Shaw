from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr
from typing import Optional

class AuthSettings(BaseSettings):
    """
    Settings required for authentication, token generation, and OAuth providers.
    """
    JWT_SECRET: SecretStr = Field(..., description="Secret key used for signing JWTs")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="TTL for short-lived access tokens")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="TTL for long-lived refresh tokens")
    
    # OAuth Keys
    GITHUB_OAUTH_CLIENT_ID: Optional[SecretStr] = Field(default=None, description="GitHub OAuth Client ID")
    GITHUB_OAUTH_CLIENT_SECRET: Optional[SecretStr] = Field(default=None, description="GitHub OAuth Client Secret")
