import os
import httpx
from typing import List, Dict
from services.llm_orchestration.application.ports import LLMProviderAdapterPort
from services.llm_orchestration.domain.entities import CompletionRequest, CompletionResponse, TokenUsage
from services.llm_orchestration.domain.exceptions import LLMProviderError, LLMRateLimitError, LLMTimeoutError, EmptyCompletionError

class OpenAIAdapter(LLMProviderAdapterPort):
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY", "mock-key")
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-3.5-turbo"

    def provider_name(self) -> str:
        return "openai"

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "content-type": "application/json"
        }
        
        messages = []
        if request.system_instruction:
            messages.append({"role": "system", "content": request.system_instruction})
        messages.extend(request.messages)
        
        payload = {
            "model": self.model,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "messages": messages,
        }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(self.base_url, headers=headers, json=payload, timeout=10.0)
        except httpx.TimeoutException:
            raise LLMTimeoutError("OpenAI API timeout")
        except httpx.RequestError as e:
            raise LLMProviderError(f"Network error calling OpenAI: {e}")
            
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", 2))
            raise LLMRateLimitError("OpenAI rate limit exceeded", retry_after=retry_after)
            
        if resp.status_code >= 500:
            raise LLMProviderError(f"OpenAI server error: {resp.status_code} {resp.text}")
            
        if resp.status_code >= 400:
            raise LLMProviderError(f"OpenAI bad request: {resp.status_code} {resp.text}")
            
        data = resp.json()
        
        try:
            content = data["choices"][0]["message"]["content"].strip()
            if not content:
                raise EmptyCompletionError("OpenAI returned empty content")
                
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            
            return CompletionResponse(
                content=content,
                usage=TokenUsage(prompt_tokens, completion_tokens, prompt_tokens + completion_tokens),
                provider_name=self.provider_name(),
                model_name=self.model
            )
        except (KeyError, IndexError) as e:
            raise LLMProviderError(f"Malformed OpenAI response: {e}")
