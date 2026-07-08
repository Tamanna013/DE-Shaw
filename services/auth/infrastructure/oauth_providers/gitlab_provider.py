from authlib.integrations.httpx_client import AsyncOAuth2Client
from services.auth.application.ports import OAuthProviderPort
from shared.config import settings

class GitLabOAuthProvider(OAuthProviderPort):
    def __init__(self):
        self.client_id = settings.oauth_gitlab_client_id
        self.client_secret = settings.oauth_gitlab_client_secret
        self.authorize_url = "https://gitlab.com/oauth/authorize"
        self.access_token_url = "https://gitlab.com/oauth/token"
        self.userinfo_url = "https://gitlab.com/api/v4/user"
        self.client = AsyncOAuth2Client(self.client_id, self.client_secret)

    async def get_authorization_url(self) -> str:
        url, _ = self.client.create_authorization_url(self.authorize_url)
        return url # type: ignore

    async def exchange_code_for_user_info(self, code: str) -> dict[str, str]:
        token = await self.client.fetch_token(self.access_token_url, code=code)
        resp = await self.client.get(self.userinfo_url, token=token)
        resp.raise_for_status()
        data = resp.json()
        
        return {
            "email": data.get("email"),
            "name": data.get("name")
        }
