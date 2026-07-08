class LLMOrchestrationError(Exception):
    """Base exception for all LLM errors."""
    pass

class LLMProviderError(LLMOrchestrationError):
    """General error returned by a provider."""
    pass

class LLMTimeoutError(LLMProviderError):
    """Timeout occurred while talking to provider."""
    pass

class LLMRateLimitError(LLMProviderError):
    """Rate limit exceeded."""
    def __init__(self, message: str, retry_after: int = 1):
        super().__init__(message)
        self.retry_after = retry_after

class EmptyCompletionError(LLMProviderError):
    """Provider returned HTTP 200 but response content is empty/whitespace."""
    pass
