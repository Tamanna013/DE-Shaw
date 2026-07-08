class DomainError(Exception):
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
