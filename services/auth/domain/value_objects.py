from dataclasses import dataclass

@dataclass(frozen=True)
class Email:
    address: str

@dataclass(frozen=True)
class HashedPassword:
    hash_value: str

@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    expires_in: int
