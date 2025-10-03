"""Tests for OAuth2 addons."""

import pytest

from turboapi_addons.oauth.base import OAuthConfig
from turboapi_addons.oauth.github import GitHubOAuthAddon, GitHubOAuthProvider
from turboapi_addons.oauth.google import GoogleOAuthAddon, GoogleOAuthProvider
from turboapi_addons.oauth.microsoft import MicrosoftOAuthAddon, MicrosoftOAuthProvider


class TestOAuthConfig:
    """Test cases for OAuthConfig."""

    def test_oauth_config_creation(self) -> None:
        """Test OAuth2 configuration creation."""
        config = OAuthConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost:8000/auth/callback",
            scope=["openid", "email", "profile"],
            additional_params={"prompt": "consent"},
        )

        assert config.client_id == "test_client_id"
        assert config.client_secret == "test_client_secret"
        assert config.redirect_uri == "http://localhost:8000/auth/callback"
        assert config.scope == ["openid", "email", "profile"]
        assert config.additional_params == {"prompt": "consent"}

    def test_oauth_config_defaults(self) -> None:
        """Test OAuth2 configuration with default values."""
        config = OAuthConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost:8000/auth/callback",
        )

        assert config.scope == []
        assert config.additional_params == {}


class TestGoogleOAuthProvider:
    """Test cases for GoogleOAuthProvider."""

    @pytest.fixture
    def google_config(self) -> OAuthConfig:
        """Create Google OAuth2 configuration."""
        return OAuthConfig(
            client_id="google_client_id",
            client_secret="google_client_secret",
            redirect_uri="http://localhost:8000/auth/google/callback",
            scope=["openid", "email", "profile"],
        )

    @pytest.fixture
    def google_provider(self, google_config: OAuthConfig) -> GoogleOAuthProvider:
        """Create Google OAuth2 provider."""
        return GoogleOAuthProvider(google_config)

    def test_google_authorization_url(self, google_provider: GoogleOAuthProvider) -> None:
        """Test Google authorization URL generation."""
        url = google_provider.get_authorization_url()

        assert "https://accounts.google.com/o/oauth2/v2/auth" in url
        assert "client_id=google_client_id" in url
        assert "redirect_uri=http%3A//localhost%3A8000/auth/google/callback" in url
        assert "scope=openid+email+profile" in url
        assert "response_type=code" in url
        assert "access_type=offline" in url
        assert "prompt=consent" in url

    def test_google_authorization_url_with_state(
        self, google_provider: GoogleOAuthProvider
    ) -> None:
        """Test Google authorization URL with custom state."""
        state = "custom_state_123"
        url = google_provider.get_authorization_url(state)

        assert f"state={state}" in url

    @pytest.mark.asyncio
    async def test_google_token_exchange_failure(
        self, google_provider: GoogleOAuthProvider
    ) -> None:
        """Test Google token exchange failure."""
        with pytest.raises(Exception, match="Token exchange failed"):
            await google_provider.exchange_code_for_token("invalid_code")

    @pytest.mark.asyncio
    async def test_google_user_info_failure(self, google_provider: GoogleOAuthProvider) -> None:
        """Test Google user info request failure."""
        with pytest.raises(Exception, match="User info request failed"):
            await google_provider.get_user_info("invalid_token")

    @pytest.mark.asyncio
    async def test_google_authentication_failure(
        self, google_provider: GoogleOAuthProvider
    ) -> None:
        """Test Google authentication failure."""
        result = await google_provider.authenticate("invalid_code")

        assert result.success is False
        assert "Google OAuth2 authentication failed" in result.error_message


class TestGitHubOAuthProvider:
    """Test cases for GitHubOAuthProvider."""

    @pytest.fixture
    def github_config(self) -> OAuthConfig:
        """Create GitHub OAuth2 configuration."""
        return OAuthConfig(
            client_id="github_client_id",
            client_secret="github_client_secret",
            redirect_uri="http://localhost:8000/auth/github/callback",
            scope=["user:email"],
        )

    @pytest.fixture
    def github_provider(self, github_config: OAuthConfig) -> GitHubOAuthProvider:
        """Create GitHub OAuth2 provider."""
        return GitHubOAuthProvider(github_config)

    def test_github_authorization_url(self, github_provider: GitHubOAuthProvider) -> None:
        """Test GitHub authorization URL generation."""
        url = github_provider.get_authorization_url()

        assert "https://github.com/login/oauth/authorize" in url
        assert "client_id=github_client_id" in url
        assert "redirect_uri=http%3A//localhost%3A8000/auth/github/callback" in url
        assert "scope=user%3Aemail" in url

    def test_github_authorization_url_with_state(
        self, github_provider: GitHubOAuthProvider
    ) -> None:
        """Test GitHub authorization URL with custom state."""
        state = "custom_state_456"
        url = github_provider.get_authorization_url(state)

        assert f"state={state}" in url

    @pytest.mark.asyncio
    async def test_github_token_exchange_failure(
        self, github_provider: GitHubOAuthProvider
    ) -> None:
        """Test GitHub token exchange failure."""
        with pytest.raises(Exception, match="Token exchange failed"):
            await github_provider.exchange_code_for_token("invalid_code")

    @pytest.mark.asyncio
    async def test_github_user_info_failure(self, github_provider: GitHubOAuthProvider) -> None:
        """Test GitHub user info request failure."""
        with pytest.raises(Exception, match="User info request failed"):
            await github_provider.get_user_info("invalid_token")

    @pytest.mark.asyncio
    async def test_github_authentication_failure(
        self, github_provider: GitHubOAuthProvider
    ) -> None:
        """Test GitHub authentication failure."""
        result = await github_provider.authenticate("invalid_code")

        assert result.success is False
        assert "GitHub OAuth2 authentication failed" in result.error_message


class TestMicrosoftOAuthProvider:
    """Test cases for MicrosoftOAuthProvider."""

    @pytest.fixture
    def microsoft_config(self) -> OAuthConfig:
        """Create Microsoft OAuth2 configuration."""
        return OAuthConfig(
            client_id="microsoft_client_id",
            client_secret="microsoft_client_secret",
            redirect_uri="http://localhost:8000/auth/microsoft/callback",
            scope=["openid", "profile", "email"],
        )

    @pytest.fixture
    def microsoft_provider(self, microsoft_config: OAuthConfig) -> MicrosoftOAuthProvider:
        """Create Microsoft OAuth2 provider."""
        return MicrosoftOAuthProvider(microsoft_config)

    def test_microsoft_authorization_url(self, microsoft_provider: MicrosoftOAuthProvider) -> None:
        """Test Microsoft authorization URL generation."""
        url = microsoft_provider.get_authorization_url()

        assert "https://login.microsoftonline.com/common/oauth2/v2.0/authorize" in url
        assert "client_id=microsoft_client_id" in url
        assert "redirect_uri=http%3A//localhost%3A8000/auth/microsoft/callback" in url
        assert "scope=openid+profile+email" in url
        assert "response_type=code" in url
        assert "response_mode=query" in url

    def test_microsoft_authorization_url_with_state(
        self, microsoft_provider: MicrosoftOAuthProvider
    ) -> None:
        """Test Microsoft authorization URL with custom state."""
        state = "custom_state_789"
        url = microsoft_provider.get_authorization_url(state)

        assert f"state={state}" in url

    @pytest.mark.asyncio
    async def test_microsoft_token_exchange_failure(
        self, microsoft_provider: MicrosoftOAuthProvider
    ) -> None:
        """Test Microsoft token exchange failure."""
        with pytest.raises(Exception, match="Token exchange failed"):
            await microsoft_provider.exchange_code_for_token("invalid_code")

    @pytest.mark.asyncio
    async def test_microsoft_user_info_failure(
        self, microsoft_provider: MicrosoftOAuthProvider
    ) -> None:
        """Test Microsoft user info request failure."""
        with pytest.raises(Exception, match="User info request failed"):
            await microsoft_provider.get_user_info("invalid_token")

    @pytest.mark.asyncio
    async def test_microsoft_authentication_failure(
        self, microsoft_provider: MicrosoftOAuthProvider
    ) -> None:
        """Test Microsoft authentication failure."""
        result = await microsoft_provider.authenticate("invalid_code")

        assert result.success is False
        assert "Microsoft OAuth2 authentication failed" in result.error_message


class TestOAuthAddons:
    """Test cases for OAuth2 addons."""

    @pytest.fixture
    def mock_application(self) -> object:
        """Create mock application."""

        class MockApplication:
            def __init__(self) -> None:
                self.container = MockContainer()

        class MockContainer:
            def register(self, name: str, factory: callable, singleton: bool = True) -> None:
                pass

        return MockApplication()

    def test_google_oauth_addon_creation(self, mock_application: object) -> None:
        """Test Google OAuth2 addon creation."""
        config = OAuthConfig(
            client_id="google_client_id",
            client_secret="google_client_secret",
            redirect_uri="http://localhost:8000/auth/google/callback",
        )

        addon = GoogleOAuthAddon(mock_application, config)

        assert addon.config == config
        assert isinstance(addon.provider, GoogleOAuthProvider)
        assert addon.get_provider_name() == "google"

    def test_github_oauth_addon_creation(self, mock_application: object) -> None:
        """Test GitHub OAuth2 addon creation."""
        config = OAuthConfig(
            client_id="github_client_id",
            client_secret="github_client_secret",
            redirect_uri="http://localhost:8000/auth/github/callback",
        )

        addon = GitHubOAuthAddon(mock_application, config)

        assert addon.config == config
        assert isinstance(addon.provider, GitHubOAuthProvider)
        assert addon.get_provider_name() == "github"

    def test_microsoft_oauth_addon_creation(self, mock_application: object) -> None:
        """Test Microsoft OAuth2 addon creation."""
        config = OAuthConfig(
            client_id="microsoft_client_id",
            client_secret="microsoft_client_secret",
            redirect_uri="http://localhost:8000/auth/microsoft/callback",
        )

        addon = MicrosoftOAuthAddon(mock_application, config)

        assert addon.config == config
        assert isinstance(addon.provider, MicrosoftOAuthProvider)
        assert addon.get_provider_name() == "microsoft"

    @pytest.mark.asyncio
    async def test_oauth_addon_configure(self, mock_application: object) -> None:
        """Test OAuth2 addon configuration."""
        config = OAuthConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost:8000/auth/callback",
        )

        addon = GoogleOAuthAddon(mock_application, config)

        # Should not raise any exceptions
        await addon.configure()

    def test_oauth_addon_authorization_url(self, mock_application: object) -> None:
        """Test OAuth2 addon authorization URL generation."""
        config = OAuthConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost:8000/auth/callback",
        )

        addon = GoogleOAuthAddon(mock_application, config)
        url = addon.get_authorization_url()

        assert "https://accounts.google.com/o/oauth2/v2/auth" in url
        assert "client_id=test_client_id" in url

    @pytest.mark.asyncio
    async def test_oauth_addon_authentication(self, mock_application: object) -> None:
        """Test OAuth2 addon authentication."""
        config = OAuthConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost:8000/auth/callback",
        )

        addon = GoogleOAuthAddon(mock_application, config)
        result = await addon.authenticate("invalid_code")

        assert result.success is False
        assert "Google OAuth2 authentication failed" in result.error_message
