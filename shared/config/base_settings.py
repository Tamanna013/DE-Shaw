from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr
from typing import Optional, Literal

class BaseServiceSettings(BaseSettings):
    """
    Common settings applicable to every TestLens service.
    """
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    ENV: Literal["dev", "staging", "prod"] = Field(default="dev", description="The deployment environment")
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO", description="Structured logging level")
    SENTRY_DSN: Optional[SecretStr] = Field(default=None, description="Optional Sentry DSN for error tracking")
    SERVICE_NAME: str = Field(..., description="The name of the running service (e.g., 'failure_analyzer')")
