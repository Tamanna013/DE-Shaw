from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

@dataclass
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

@dataclass
class CompletionRequest:
    # A generic request payload, usually templated from somewhere else
    system_instruction: Optional[str]
    messages: List[Dict[str, str]]
    max_tokens: int = 1000
    temperature: float = 0.0

@dataclass
class CompletionResponse:
    content: str
    usage: TokenUsage
    provider_name: str
    model_name: str
