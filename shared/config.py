from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Config(BaseSettings):
    jwt_secret: str = Field('super-secret-key-for-dev', env='JWT_SECRET')
    jwt_algorithm: str = Field('HS256', env='JWT_ALGORITHM')
    access_token_ttl_seconds: int = Field(900, env='ACCESS_TOKEN_TTL_SECONDS')
    refresh_token_ttl_seconds: int = Field(86400, env='REFRESH_TOKEN_TTL_SECONDS')
    oauth_github_client_id: str = Field('', env='OAUTH_GITHUB_CLIENT_ID')
    oauth_github_client_secret: str = Field('', env='OAUTH_GITHUB_CLIENT_SECRET')
    oauth_gitlab_client_id: str = Field('', env='OAUTH_GITLAB_CLIENT_ID')
    oauth_gitlab_client_secret: str = Field('', env='OAUTH_GITLAB_CLIENT_SECRET')
    database_url: str = Field('postgresql+asyncpg://postgres:postgres@localhost:5432/testlens', env='DATABASE_URL')
    redis_url: str = Field('redis://localhost:6379/0', env='REDIS_URL')

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

settings = Config()
