"""Base classes for OAuth2 addons."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from turboapi.security.interfaces import AuthResult


@dataclass
class OAuthConfig:
    """
    Configuration for OAuth2 providers.

    Parameters
    ----------
    client_id : str
        OAuth2 client ID.
    client_secret : str
        OAuth2 client secret.
    redirect_uri : str
        OAuth2 redirect URI.
    scope : list[str], optional
        OAuth2 scopes to request.
    additional_params : dict[str, Any], optional
        Additional parameters for OAuth2 flow.
    """

    client_id: str
    client_secret: str
    redirect_uri: str
    scope: list[str] | None = None
    additional_params: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.scope is None:
            self.scope = []
        if self.additional_params is None:
            self.additional_params = {}


class OAuthProvider(ABC):
    """
    Base interface for OAuth2 providers.

    Defines methods for OAuth2 authentication flow including
    authorization URL generation, token exchange, and user info retrieval.
    """

    @abstractmethod
    def get_authorization_url(self, state: str | None = None) -> str:
        """
        Generate OAuth2 authorization URL.

        Parameters
        ----------
        state : str, optional
            State parameter for CSRF protection.

        Returns
        -------
        str
            Authorization URL.
        """
        ...

    @abstractmethod
    async def exchange_code_for_token(self, code: str) -> dict[str, Any]:
        """
        Exchange authorization code for access token.

        Parameters
        ----------
        code : str
            Authorization code from OAuth2 provider.

        Returns
        -------
        dict[str, Any]
            Token response containing access token and related data.
        """
        ...

    @abstractmethod
    async def get_user_info(self, access_token: str) -> dict[str, Any]:
        """
        Get user information using access token.

        Parameters
        ----------
        access_token : str
            OAuth2 access token.

        Returns
        -------
        dict[str, Any]
            User information from OAuth2 provider.
        """
        ...

    @abstractmethod
    async def authenticate(self, code: str) -> AuthResult:
        """
        Complete OAuth2 authentication flow.

        Parameters
        ----------
        code : str
            Authorization code from OAuth2 provider.

        Returns
        -------
        AuthResult
            Authentication result with user information.
        """
        ...


class BaseOAuthAddon:
    """
    Base class for OAuth2 addons.

    Provides common functionality for OAuth2 provider implementations
    and integrates with the TurboAPI security system.
    """

    def __init__(self, application: Any, config: OAuthConfig) -> None:
        """
        Initialize OAuth2 addon.

        Parameters
        ----------
        application : Any
            TurboAPI application instance.
        config : OAuthConfig
            OAuth2 configuration.
        """
        self.application = application
        self.config = config
        self.provider = self._create_provider()

    @abstractmethod
    def _create_provider(self) -> OAuthProvider:
        """
        Create OAuth2 provider instance.

        Returns
        -------
        OAuthProvider
            OAuth2 provider instance.
        """
        ...

    def get_provider_name(self) -> str:
        """
        Get the name of the OAuth2 provider.

        Returns
        -------
        str
            Provider name (e.g., 'google', 'github').
        """
        return self.provider.__class__.__name__.lower().replace("provider", "")

    def configure(self) -> None:
        """Configure OAuth2 addon."""
        # Register OAuth2 provider in DI container
        provider_name = f"oauth_{self.get_provider_name()}_provider"
        self.application.container.register(provider_name, lambda: self.provider, singleton=True)

    def get_authorization_url(self, state: str | None = None) -> str:
        """
        Generate OAuth2 authorization URL.

        Parameters
        ----------
        state : str, optional
            State parameter for CSRF protection.

        Returns
        -------
        str
            Authorization URL.
        """
        return self.provider.get_authorization_url(state)

    async def authenticate(self, code: str) -> AuthResult:
        """
        Complete OAuth2 authentication flow.

        Parameters
        ----------
        code : str
            Authorization code from OAuth2 provider.

        Returns
        -------
        AuthResult
            Authentication result with user information.
        """
        return await self.provider.authenticate(code)
