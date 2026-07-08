# TestLens Authentication Module

Provides JWT authentication, password hashing, OAuth2 via GitHub/GitLab, and Redis-based rate limiting and session revocation.

## Setup

```bash
pip install -r requirements.txt
uvicorn services.auth.main:app --reload
```

## Environment Variables

| Variable | Description |
|---|---|
| JWT_SECRET | Secret for signing JWTs |
| JWT_ALGORITHM | e.g. HS256 |
| ACCESS_TOKEN_TTL_SECONDS | Access token lifespan (default 900) |
| REFRESH_TOKEN_TTL_SECONDS | Refresh token lifespan (default 86400) |
| DATABASE_URL | Postgres connection string |
| REDIS_URL | Redis connection string |
| OAUTH_GITHUB_CLIENT_ID | GitHub OAuth App ID |
| OAUTH_GITHUB_CLIENT_SECRET | GitHub OAuth Secret |

## Login & Refresh Sequence

```mermaid
sequenceDiagram
    Client->>API: POST /api/v1/auth/login {email, pwd}
    API->>DB: Get user by email
    API->>API: Verify password hash
    API->>Redis: Clear failed login attempts
    API->>API: Sign JWT Access & Refresh
    API-->>Client: 200 OK {access_token, refresh_token}
    
    Client->>API: POST /api/v1/auth/refresh {refresh_token}
    API->>API: Verify Refresh JWT
    API->>Redis: Check if refresh token is blocked
    API->>Redis: Block old refresh token
    API->>API: Sign new JWTs
    API-->>Client: 200 OK {new_access, new_refresh}
```
