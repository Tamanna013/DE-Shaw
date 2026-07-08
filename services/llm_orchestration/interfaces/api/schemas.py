from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class CompletionRequestSchema(BaseModel):
    system_instruction: Optional[str] = None
    messages: List[Dict[str, str]]
    max_tokens: int = Field(default=1000)
    temperature: float = Field(default=0.0)

class TokenUsageSchema(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class CompletionResponseSchema(BaseModel):
    content: str
    usage: TokenUsageSchema
    provider_name: str
    model_name: str
