"""Google OAuth2 addon for TurboAPI."""

import secrets
from datetime import datetime
from typing import Any

from turboapi.security.interfaces import AuthResult, User

from .base import BaseOAuthAddon, OAuthConfig, OAuthProvider


class GoogleOAuthProvider(OAuthProvider):
    """
    Google OAuth2 provider implementation.

    Handles Google OAuth2 authentication flow including
    authorization URL generation, token exchange, and user info retrieval.
    """

    def __init__(self, config: OAuthConfig) -> None:
        """
        Initialize Google OAuth2 provider.

        Parameters
        ----------
        config : OAuthConfig
            OAuth2 configuration.
        """
        self.config = config
        self.base_url = "https://accounts.google.com"
        self.api_url = "https://www.googleapis.com"

    def get_authorization_url(self, state: str | None = None) -> str:
        """
        Generate Google OAuth2 authorization URL.

        Parameters
        ----------
        state : str, optional
            State parameter for CSRF protection.

        Returns
        -------
        str
            Google OAuth2 authorization URL.
        """
        if state is None:
            state = secrets.token_urlsafe(32)

        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": " ".join(self.config.scope or ["openid", "email", "profile"]),
            "response_type": "code",
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }

        # Add additional parameters
        if self.config.additional_params:
            params.update(self.config.additional_params)

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.base_url}/o/oauth2/v2/auth?{query_string}"

    async def exchange_code_for_token(self, code: str) -> dict[str, Any]:
        """
        Exchange authorization code for Google access token.

        Parameters
        ----------
        code : str
            Authorization code from Google.

        Returns
        -------
        dict[str, Any]
            Token response containing access token and related data.
        """
        import aiohttp

        token_url = f"{self.base_url}/o/oauth2/token"

        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.config.redirect_uri,
        }

        async with (
            aiohttp.ClientSession() as session,
            session.post(token_url, data=data) as response,
        ):
            if response.status != 200:
                raise Exception(f"Token exchange failed: {response.status}")

            return await response.json()  # type: ignore[no-any-return]

    async def get_user_info(self, access_token: str) -> dict[str, Any]:
        """
        Get user information from Google using access token.

        Parameters
        ----------
        access_token : str
            Google OAuth2 access token.

        Returns
        -------
        dict[str, Any]
            User information from Google.
        """
        import aiohttp

        user_info_url = f"{self.api_url}/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}

        async with (
            aiohttp.ClientSession() as session,
            session.get(user_info_url, headers=headers) as response,
        ):
            if response.status != 200:
                raise Exception(f"User info request failed: {response.status}")

            return await response.json()  # type: ignore[no-any-return]

    async def authenticate(self, code: str) -> AuthResult:
        """
        Complete Google OAuth2 authentication flow.

        Parameters
        ----------
        code : str
            Authorization code from Google.

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
                    success=False, error_message="No access token received from Google"
                )

            # Get user information
            user_info = await self.get_user_info(access_token)

            # Create user object
            user = User(
                id=user_info.get("id", ""),
                username=user_info.get("email", ""),
                email=user_info.get("email", ""),
                is_active=True,
                is_verified=user_info.get("verified_email", False),
                roles=[],
                permissions=[],
                created_at=datetime.now(),  # Will be updated by the system
                extra_data={
                    "name": user_info.get("name", ""),
                    "picture": user_info.get("picture", ""),
                    "locale": user_info.get("locale", ""),
                    "provider": "google",
                },
            )

            return AuthResult(
                success=True,
                user_id=user.id,
                access_token=access_token,
                expires_at=None,  # Google tokens don't have explicit expiration
                # extra_claims={
                #     "provider": "google",
                #     "email": user.email,
                #     "name": user_info.get("name", ""),
                # },
            )

        except Exception as e:
            return AuthResult(
                success=False, error_message=f"Google OAuth2 authentication failed: {str(e)}"
            )


class GoogleOAuthAddon(BaseOAuthAddon):
    """
    Google OAuth2 addon for TurboAPI.

    Provides Google OAuth2 authentication integration with TurboAPI.
    """

    def _create_provider(self) -> GoogleOAuthProvider:
        """
        Create Google OAuth2 provider instance.

        Returns
        -------
        GoogleOAuthProvider
            Google OAuth2 provider instance.
        """
        return GoogleOAuthProvider(self.config)
