class AIReasoningError(Exception):
    pass

class MissingContextError(AIReasoningError):
    pass

class LLMProviderError(AIReasoningError):
    pass
