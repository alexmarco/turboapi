"""Microsoft OAuth2 addon for TurboAPI."""

import secrets
from datetime import datetime
from typing import Any

from turboapi.security.interfaces import AuthResult
from turboapi.security.interfaces import User

from .base import BaseOAuthAddon
from .base import OAuthConfig
from .base import OAuthProvider


class MicrosoftOAuthProvider(OAuthProvider):
    """
    Microsoft OAuth2 provider implementation.

    Handles Microsoft OAuth2 authentication flow including
    authorization URL generation, token exchange, and user info retrieval.
    """

    def __init__(self, config: OAuthConfig) -> None:
        """
        Initialize Microsoft OAuth2 provider.

        Parameters
        ----------
        config : OAuthConfig
            OAuth2 configuration.
        """
        self.config = config
        self.base_url = "https://login.microsoftonline.com/common/oauth2/v2.0"
        self.api_url = "https://graph.microsoft.com/v1.0"

    def get_authorization_url(self, state: str | None = None) -> str:
        """
        Generate Microsoft OAuth2 authorization URL.

        Parameters
        ----------
        state : str, optional
            State parameter for CSRF protection.

        Returns
        -------
        str
            Microsoft OAuth2 authorization URL.
        """
        if state is None:
            state = secrets.token_urlsafe(32)

        params = {
            "client_id": self.config.client_id,
            "response_type": "code",
            "redirect_uri": self.config.redirect_uri,
            "scope": " ".join(self.config.scope or ["openid", "profile", "email"]),
            "state": state,
            "response_mode": "query",
        }

        # Add additional parameters
        if self.config.additional_params:
            params.update(self.config.additional_params)

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.base_url}/authorize?{query_string}"

    async def exchange_code_for_token(self, code: str) -> dict[str, Any]:
        """
        Exchange authorization code for Microsoft access token.

        Parameters
        ----------
        code : str
            Authorization code from Microsoft.

        Returns
        -------
        dict[str, Any]
            Token response containing access token and related data.
        """
        import aiohttp

        token_url = f"{self.base_url}/token"

        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.config.redirect_uri,
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        async with (
            aiohttp.ClientSession() as session,
            session.post(token_url, data=data, headers=headers) as response,
        ):
            if response.status != 200:
                raise Exception(f"Token exchange failed: {response.status}")

            return await response.json()  # type: ignore[no-any-return]

    async def get_user_info(self, access_token: str) -> dict[str, Any]:
        """
        Get user information from Microsoft using access token.

        Parameters
        ----------
        access_token : str
            Microsoft OAuth2 access token.

        Returns
        -------
        dict[str, Any]
            User information from Microsoft.
        """
        import aiohttp

        user_info_url = f"{self.api_url}/me"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        async with (
            aiohttp.ClientSession() as session,
            session.get(user_info_url, headers=headers) as response,
        ):
            if response.status != 200:
                raise Exception(f"User info request failed: {response.status}")

            return await response.json()  # type: ignore[no-any-return]

    async def authenticate(self, code: str) -> AuthResult:
        """
        Complete Microsoft OAuth2 authentication flow.

        Parameters
        ----------
        code : str
            Authorization code from Microsoft.

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
                    success=False, error_message="No access token received from Microsoft"
                )

            # Get user information
            user_info = await self.get_user_info(access_token)

            # Create user object
            user = User(
                id=user_info.get("id", ""),
                username=user_info.get("userPrincipalName", ""),
                email=user_info.get("mail", user_info.get("userPrincipalName", "")),
                is_active=True,
                is_verified=True,  # Microsoft accounts are typically verified
                roles=[],
                permissions=[],
                created_at=datetime.now(),  # Will be updated by the system
                extra_data={
                    "display_name": user_info.get("displayName", ""),
                    "given_name": user_info.get("givenName", ""),
                    "surname": user_info.get("surname", ""),
                    "job_title": user_info.get("jobTitle", ""),
                    "office_location": user_info.get("officeLocation", ""),
                    "preferred_language": user_info.get("preferredLanguage", ""),
                    "business_phones": user_info.get("businessPhones", []),
                    "mobile_phone": user_info.get("mobilePhone", ""),
                    "provider": "microsoft",
                },
            )

            return AuthResult(
                success=True,
                user_id=user.id,
                access_token=access_token,
                expires_at=None,  # Microsoft tokens have expiration in token_data
                # extra_claims={
                #     "provider": "microsoft",
                #     "email": user.email,
                #     "name": user_info.get("displayName", ""),
                #     "upn": user_info.get("userPrincipalName", ""),
                # },
            )

        except Exception as e:
            return AuthResult(
                success=False, error_message=f"Microsoft OAuth2 authentication failed: {str(e)}"
            )


class MicrosoftOAuthAddon(BaseOAuthAddon):
    """
    Microsoft OAuth2 addon for TurboAPI.

    Provides Microsoft OAuth2 authentication integration with TurboAPI.
    """

    def _create_provider(self) -> MicrosoftOAuthProvider:
        """
        Create Microsoft OAuth2 provider instance.

        Returns
        -------
        MicrosoftOAuthProvider
            Microsoft OAuth2 provider instance.
        """
        return MicrosoftOAuthProvider(self.config)
