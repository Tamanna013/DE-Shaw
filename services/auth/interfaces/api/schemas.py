from pydantic import BaseModel, EmailStr, field_validator
import re

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 12:
            raise ValueError("Password must be at least 12 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least 1 uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least 1 lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least 1 digit")
        if not re.search(r"[^\w\s]", v):
            raise ValueError("Password must contain at least 1 symbol")
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int

class UserProfileResponse(BaseModel):
    id: str
    email: str
    full_name: str
