import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from services.auth.interfaces.api.schemas import RegisterRequest, LoginRequest, RefreshRequest, TokenResponse, UserProfileResponse
from services.auth.interfaces.api.dependencies import get_user_repository, get_token_store, get_current_user
from services.auth.application.use_cases.register_user import RegisterUserUseCase
from services.auth.application.use_cases.login_with_password import LoginWithPasswordUseCase
from services.auth.application.use_cases.login_with_oauth import LoginWithOAuthUseCase
from services.auth.application.use_cases.refresh_token import RefreshTokenUseCase
from services.auth.application.use_cases.revoke_session import RevokeSessionUseCase
from services.auth.infrastructure.oauth_providers.github_provider import GitHubOAuthProvider
from services.auth.infrastructure.oauth_providers.gitlab_provider import GitLabOAuthProvider
from services.auth.domain.exceptions import DomainError, RateLimitExceededError, InvalidCredentialsError, DuplicateEmailError, InvalidTokenError
from services.auth.domain.entities import User
from shared.logging_engine import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

def get_oauth_provider(provider: str):
    if provider == "github":
        return GitHubOAuthProvider()
    elif provider == "gitlab":
        return GitLabOAuthProvider()
    raise HTTPException(status_code=400, detail="Unsupported OAuth provider")

def format_error(code: str, message: str) -> dict:
    return {"error": {"code": code, "message": message, "trace_id": str(uuid.uuid4())}}

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserProfileResponse)
async def register(req: RegisterRequest, user_repo=Depends(get_user_repository)):
    use_case = RegisterUserUseCase(user_repo)
    try:
        user = await use_case.execute(req.email, req.password, req.full_name)
        return UserProfileResponse(id=user.id, email=user.email, full_name=user.full_name)
    except DuplicateEmailError as e:
        raise HTTPException(status_code=409, detail=format_error("DUPLICATE_EMAIL", str(e)))
    except DomainError as e:
        raise HTTPException(status_code=400, detail=format_error("DOMAIN_ERROR", str(e)))

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, request: Request, user_repo=Depends(get_user_repository), token_store=Depends(get_token_store)):
    use_case = LoginWithPasswordUseCase(user_repo, token_store)
    try:
        tokens = await use_case.execute(req.email, req.password, ip=request.client.host if request.client else "0.0.0.0")
        return TokenResponse(access_token=tokens.access_token, refresh_token=tokens.refresh_token, expires_in=tokens.expires_in)
    except RateLimitExceededError as e:
        raise HTTPException(status_code=429, detail=format_error("RATE_LIMIT_EXCEEDED", str(e)), headers={"Retry-After": str(e.retry_after)})
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=401, detail=format_error("INVALID_CREDENTIALS", str(e)))

@router.get("/oauth/{provider}/authorize")
async def oauth_authorize(provider: str):
    oauth_provider = get_oauth_provider(provider)
    url = await oauth_provider.get_authorization_url()
    return RedirectResponse(url)

@router.get("/oauth/{provider}/callback", response_model=TokenResponse)
async def oauth_callback(provider: str, code: str, request: Request, user_repo=Depends(get_user_repository)):
    oauth_provider = get_oauth_provider(provider)
    use_case = LoginWithOAuthUseCase(user_repo, oauth_provider)
    try:
        tokens = await use_case.execute(code, ip=request.client.host if request.client else "0.0.0.0")
        return TokenResponse(access_token=tokens.access_token, refresh_token=tokens.refresh_token, expires_in=tokens.expires_in)
    except Exception as e:
        logger.error(f"OAuth error: {e}")
        raise HTTPException(status_code=500, detail=format_error("OAUTH_ERROR", str(e)))

@router.post("/refresh", response_model=TokenResponse)
async def refresh(req: RefreshRequest, request: Request, user_repo=Depends(get_user_repository), token_store=Depends(get_token_store)):
    use_case = RefreshTokenUseCase(user_repo, token_store)
    try:
        tokens = await use_case.execute(req.refresh_token, ip=request.client.host if request.client else "0.0.0.0")
        return TokenResponse(access_token=tokens.access_token, refresh_token=tokens.refresh_token, expires_in=tokens.expires_in)
    except InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=format_error("INVALID_TOKEN", str(e)))

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(req: RefreshRequest, token_store=Depends(get_token_store)):
    use_case = RevokeSessionUseCase(token_store)
    await use_case.execute(req.refresh_token)
    return None

@router.get("/me", response_model=UserProfileResponse)
async def get_me(user: User = Depends(get_current_user)):
    return UserProfileResponse(id=user.id, email=user.email, full_name=user.full_name)
