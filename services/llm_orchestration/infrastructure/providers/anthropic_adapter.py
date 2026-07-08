import os
import httpx
from typing import List, Dict
from services.llm_orchestration.application.ports import LLMProviderAdapterPort
from services.llm_orchestration.domain.entities import CompletionRequest, CompletionResponse, TokenUsage
from services.llm_orchestration.domain.exceptions import LLMProviderError, LLMRateLimitError, LLMTimeoutError, EmptyCompletionError

class AnthropicAdapter(LLMProviderAdapterPort):
    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "mock-key")
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-haiku-20240307"

    def provider_name(self) -> str:
        return "anthropic"

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "messages": request.messages,
            "system": request.system_instruction
        }

        # Remove None values
        if not payload["system"]:
            del payload["system"]

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(self.base_url, headers=headers, json=payload, timeout=10.0)
        except httpx.TimeoutException:
            raise LLMTimeoutError("Anthropic API timeout")
        except httpx.RequestError as e:
            raise LLMProviderError(f"Network error calling Anthropic: {e}")
            
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", 2))
            raise LLMRateLimitError("Anthropic rate limit exceeded", retry_after=retry_after)
            
        if resp.status_code >= 500:
            raise LLMProviderError(f"Anthropic server error: {resp.status_code} {resp.text}")
            
        if resp.status_code >= 400:
            raise LLMProviderError(f"Anthropic bad request: {resp.status_code} {resp.text}")
            
        data = resp.json()
        
        try:
            content = data["content"][0]["text"].strip()
            if not content:
                raise EmptyCompletionError("Anthropic returned empty content")
                
            usage = data.get("usage", {})
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            
            return CompletionResponse(
                content=content,
                usage=TokenUsage(input_tokens, output_tokens, input_tokens + output_tokens),
                provider_name=self.provider_name(),
                model_name=self.model
            )
        except (KeyError, IndexError) as e:
            raise LLMProviderError(f"Malformed Anthropic response: {e}")
