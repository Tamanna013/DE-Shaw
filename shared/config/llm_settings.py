from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr
from typing import Optional

class LLMSettings(BaseSettings):
    """
    Settings required exclusively by the LLM Orchestration module.
    """
    PRIMARY_PROVIDER: str = Field(default="anthropic", description="Primary LLM provider (anthropic|openai)")
    ANTHROPIC_API_KEY: Optional[SecretStr] = Field(default=None, description="Anthropic API Key")
    OPENAI_API_KEY: Optional[SecretStr] = Field(default=None, description="OpenAI API Key (Fallback)")
    
    # Budget Controls
    MAX_TOKENS_PER_REQUEST: int = Field(default=4000, description="Hard cap on token generation per request")
    MAX_RETRIES: int = Field(default=3, description="Number of times to retry 5xx/429 errors before giving up")
