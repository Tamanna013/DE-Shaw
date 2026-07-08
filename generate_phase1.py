import os

files = {
    'shared/config.py': '''from pydantic_settings import BaseSettings, SettingsConfigDict
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
''',

    'shared/logging_engine.py': '''import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        if hasattr(record, 'trace_id'):
            log_data['trace_id'] = record.trace_id # type: ignore
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id # type: ignore
        if hasattr(record, 'ip'):
            log_data['ip'] = record.ip # type: ignore
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Redact password if present in message (though we avoid logging it entirely)
        msg = log_data['message'].lower()
        if 'password' in msg:
            log_data['message'] = '*** REDACTED ***'
            
        return json.dumps(log_data)

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
''',

    'services/auth/domain/entities.py': '''from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class User:
    id: str
    email: str
    full_name: str
    hashed_password: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Session:
    user_id: str
    refresh_token_jti: str
    expires_at: datetime
    revoked: bool = False

@dataclass
class BlockedDomain:
    domain: str
''',

    'services/auth/domain/value_objects.py': '''from dataclasses import dataclass

@dataclass(frozen=True)
class Email:
    address: str

@dataclass(frozen=True)
class HashedPassword:
    hash_value: str

@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    expires_in: int
''',

    'services/auth/domain/exceptions.py': '''class DomainError(Exception):
    pass

class InvalidCredentialsError(DomainError):
    pass

class TokenExpiredError(DomainError):
    pass

class InvalidTokenError(DomainError):
    pass

class AccountLinkingRequiredError(DomainError):
    def __init__(self, provider: str, email: str):
        super().__init__(f"Account linking required for {email} via {provider}")
        self.provider = provider
        self.email = email

class DuplicateEmailError(DomainError):
    pass

class RateLimitExceededError(DomainError):
    def __init__(self, retry_after: int):
        super().__init__("Too many requests")
        self.retry_after = retry_after

class InvalidRoleError(DomainError):
    pass
''',

    'services/auth/application/ports.py': '''from typing import Protocol, Optional, runtime_checkable
from services.auth.domain.entities import User, BlockedDomain
from services.auth.domain.value_objects import Email

@runtime_checkable
class UserRepositoryPort(Protocol):
    async def get_by_id(self, user_id: str) -> Optional[User]: ...
    async def get_by_email(self, email: Email) -> Optional[User]: ...
    async def create(self, user: User) -> User: ...
    async def get_blocked_domain(self, domain: str) -> Optional[BlockedDomain]: ...

@runtime_checkable
class TokenStorePort(Protocol):
    async def block_refresh_token(self, jti: str, ttl_seconds: int) -> None: ...
    async def is_refresh_token_blocked(self, jti: str) -> bool: ...
    async def record_failed_login(self, email: Email) -> int: ...
    async def get_failed_logins(self, email: Email) -> int: ...
    async def clear_failed_logins(self, email: Email) -> None: ...

@runtime_checkable
class OAuthProviderPort(Protocol):
    async def get_authorization_url(self) -> str: ...
    async def exchange_code_for_user_info(self, code: str) -> dict[str, str]: ...
'''
}

for filepath, content in files.items():
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Phase 1 files generated successfully.")
