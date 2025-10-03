"""GitHub OAuth2 addon for TurboAPI."""

import secrets
from datetime import datetime
from typing import Any

from turboapi.security.interfaces import AuthResult
from turboapi.security.interfaces import User

from .base import BaseOAuthAddon
from .base import OAuthConfig
from .base import OAuthProvider


class GitHubOAuthProvider(OAuthProvider):
    """
    GitHub OAuth2 provider implementation.

    Handles GitHub OAuth2 authentication flow including
    authorization URL generation, token exchange, and user info retrieval.
    """

    def __init__(self, config: OAuthConfig) -> None:
        """
        Initialize GitHub OAuth2 provider.

        Parameters
        ----------
        config : OAuthConfig
            OAuth2 configuration.
        """
        self.config = config
        self.base_url = "https://github.com"
        self.api_url = "https://api.github.com"

    def get_authorization_url(self, state: str | None = None) -> str:
        """
        Generate GitHub OAuth2 authorization URL.

        Parameters
        ----------
        state : str, optional
            State parameter for CSRF protection.

        Returns
        -------
        str
            GitHub OAuth2 authorization URL.
        """
        if state is None:
            state = secrets.token_urlsafe(32)

        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": ",".join(self.config.scope or ["user:email"]),
            "state": state,
        }

        # Add additional parameters
        if self.config.additional_params:
            params.update(self.config.additional_params)

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.base_url}/login/oauth/authorize?{query_string}"

    async def exchange_code_for_token(self, code: str) -> dict[str, Any]:
        """
        Exchange authorization code for GitHub access token.

        Parameters
        ----------
        code : str
            Authorization code from GitHub.

        Returns
        -------
        dict[str, Any]
            Token response containing access token and related data.
        """
        import aiohttp

        token_url = f"{self.base_url}/login/oauth/access_token"

        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "redirect_uri": self.config.redirect_uri,
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        async with (
            aiohttp.ClientSession() as session,
            session.post(token_url, json=data, headers=headers) as response,
        ):
            if response.status != 200:
                raise Exception(f"Token exchange failed: {response.status}")

            return await response.json()  # type: ignore[no-any-return]

    async def get_user_info(self, access_token: str) -> dict[str, Any]:
        """
        Get user information from GitHub using access token.

        Parameters
        ----------
        access_token : str
            GitHub OAuth2 access token.

        Returns
        -------
        dict[str, Any]
            User information from GitHub.
        """
        import aiohttp

        user_info_url = f"{self.api_url}/user"
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        async with (
            aiohttp.ClientSession() as session,
            session.get(user_info_url, headers=headers) as response,
        ):
            if response.status != 200:
                raise Exception(f"User info request failed: {response.status}")

            user_data = await response.json()

            # Get user emails
            emails_url = f"{self.api_url}/user/emails"
            async with session.get(emails_url, headers=headers) as email_response:
                if email_response.status == 200:
                    emails_data = await email_response.json()
                    user_data["emails"] = emails_data

            return user_data  # type: ignore[no-any-return]

    async def authenticate(self, code: str) -> AuthResult:
        """
        Complete GitHub OAuth2 authentication flow.

        Parameters
        ----------
        code : str
            Authorization code from GitHub.

        Returns
        -------
        AuthResult
            Authentication result with user information.
        """
        try:
            # Exchange code for token
            token_data = await self.exchange_code_for_token(code)
            access_token = token_data.get("access_token")

            if not access_token:
                return AuthResult(
                    success=False, error_message="No access token received from GitHub"
                )

            # Get user information
            user_info = await self.get_user_info(access_token)

            # Get primary email
            primary_email = user_info.get("email", "")
            if not primary_email and user_info.get("emails"):
                for email_data in user_info["emails"]:
                    if email_data.get("primary", False):
                        primary_email = email_data.get("email", "")
                        break

            # Create user object
            user = User(
                id=str(user_info.get("id", "")),
                username=user_info.get("login", ""),
                email=primary_email,
                is_active=True,
                is_verified=user_info.get("email_verified", True),
                roles=[],
                permissions=[],
                created_at=datetime.now(),  # Will be updated by the system
                extra_data={
                    "name": user_info.get("name", ""),
                    "avatar_url": user_info.get("avatar_url", ""),
                    "bio": user_info.get("bio", ""),
                    "location": user_info.get("location", ""),
                    "company": user_info.get("company", ""),
                    "blog": user_info.get("blog", ""),
                    "public_repos": user_info.get("public_repos", 0),
                    "followers": user_info.get("followers", 0),
                    "following": user_info.get("following", 0),
                    "provider": "github",
                },
            )

            return AuthResult(
                success=True,
                user_id=user.id,
                access_token=access_token,
                expires_at=None,  # GitHub tokens don't have explicit expiration
                # extra_claims={
                #     "provider": "github",
                #     "username": user.username,
                #     "email": user.email,
                #     "name": user_info.get("name", ""),
                # },
            )

        except Exception as e:
            return AuthResult(
                success=False, error_message=f"GitHub OAuth2 authentication failed: {str(e)}"
            )


class GitHubOAuthAddon(BaseOAuthAddon):
    """
    GitHub OAuth2 addon for TurboAPI.

    Provides GitHub OAuth2 authentication integration with TurboAPI.
    """

    def _create_provider(self) -> GitHubOAuthProvider:
        """
        Create GitHub OAuth2 provider instance.

        Returns
        -------
        GitHubOAuthProvider
            GitHub OAuth2 provider instance.
        """
        return GitHubOAuthProvider(self.config)
