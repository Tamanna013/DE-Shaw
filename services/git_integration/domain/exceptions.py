class GitIntegrationError(Exception):
    pass

class ProviderAPIError(GitIntegrationError):
    def __init__(self, message: str, status_code: int = 500, rate_limit_remaining: int = -1):
        super().__init__(message)
        self.status_code = status_code
        self.rate_limit_remaining = rate_limit_remaining

class RateLimitExceededError(ProviderAPIError):
    pass

class InvalidWebhookSignatureError(GitIntegrationError):
    pass

class CloneManagerError(GitIntegrationError):
    pass

class CommitNotFoundError(GitIntegrationError):
    pass

class RepositoryNotInstalledError(GitIntegrationError):
    """Raised when GitHub App is not installed on the requested repo."""
    pass
