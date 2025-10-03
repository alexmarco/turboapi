"""Pruebas para la implementación JWT de autenticación."""

import time
from datetime import datetime
from unittest.mock import AsyncMock
from unittest.mock import Mock

import pytest

from turboapi.security.interfaces import AuthResult
from turboapi.security.interfaces import TokenPayload
from turboapi.security.interfaces import User


class TestJWTTokenManager:
    """Pruebas para JWTTokenManager."""

    @pytest.fixture
    def jwt_config(self) -> dict:
        """Configuración de prueba para JWT."""
        return {
            "secret": "test_secret_key_123",
            "algorithm": "HS256",
            "access_token_expire_minutes": 30,
            "refresh_token_expire_days": 7,
        }

    @pytest.fixture
    def token_manager(self, jwt_config):
        """Fixture para JWTTokenManager."""
        from turboapi.security.jwt import JWTTokenManager

        return JWTTokenManager(**jwt_config)

    @pytest.fixture
    def sample_payload(self) -> dict:
        """Payload de prueba para tokens."""
        return {
            "user_id": "123",
            "username": "john_doe",
            "roles": ["user"],
            "permissions": ["read"],
        }

    def test_generate_access_token(self, token_manager, sample_payload):
        """Prueba la generación de tokens de acceso."""
        token = token_manager.generate_access_token(sample_payload)

        assert isinstance(token, str)
        assert len(token) > 50  # JWT should be reasonably long
        assert token.count(".") == 2  # JWT format: header.payload.signature

    def test_verify_access_token(self, token_manager, sample_payload):
        """Prueba la verificación de tokens de acceso."""
        token = token_manager.generate_access_token(sample_payload)
        decoded_payload = token_manager.verify_access_token(token)

        assert isinstance(decoded_payload, TokenPayload)
        assert decoded_payload.user_id == sample_payload["user_id"]
        assert decoded_payload.username == sample_payload["username"]
        assert decoded_payload.roles == sample_payload["roles"]
        assert decoded_payload.permissions == sample_payload["permissions"]

    def test_generate_refresh_token(self, token_manager):
        """Prueba la generación de tokens de renovación."""
        user_id = "123"
        token = token_manager.generate_refresh_token(user_id)

        assert isinstance(token, str)
        assert len(token) > 50
        assert token.count(".") == 2

    def test_verify_refresh_token(self, token_manager):
        """Prueba la verificación de tokens de renovación."""
        user_id = "123"
        token = token_manager.generate_refresh_token(user_id)
        decoded_user_id = token_manager.verify_refresh_token(token)

        assert decoded_user_id == user_id

    def test_invalid_token_raises_exception(self, token_manager):
        """Prueba que tokens inválidos lancen excepción."""
        from turboapi.security.exceptions import InvalidTokenError

        with pytest.raises(InvalidTokenError):
            token_manager.verify_access_token("invalid_token")

    def test_expired_token_raises_exception(self, jwt_config):
        """Prueba que tokens expirados lancen excepción."""
        from turboapi.security.exceptions import InvalidTokenError
        from turboapi.security.jwt import JWTTokenManager

        # Configurar token que expire inmediatamente
        config = jwt_config.copy()
        config["access_token_expire_minutes"] = -1  # Expira en el pasado

        token_manager = JWTTokenManager(**config)
        token = token_manager.generate_access_token({"user_id": "123"})

        with pytest.raises(InvalidTokenError):
            token_manager.verify_access_token(token)

    @pytest.mark.asyncio
    async def test_revoke_token(self, token_manager, sample_payload):
        """Prueba la revocación de tokens."""
        token = token_manager.generate_access_token(sample_payload)

        # El token debería ser válido inicialmente
        decoded = token_manager.verify_access_token(token)
        assert decoded.user_id == sample_payload["user_id"]

        # Revocar el token
        result = await token_manager.revoke_token(token)
        assert result is True

        # El token revocado debería ser inválido
        from turboapi.security.exceptions import InvalidTokenError

        with pytest.raises(InvalidTokenError):
            token_manager.verify_access_token(token)


class TestJWTAuthProvider:
    """Pruebas para JWTAuthProvider."""

    @pytest.fixture
    def auth_config(self) -> dict:
        """Configuración de prueba para autenticación."""
        return {
            "jwt_secret": "test_secret_key_123",
            "jwt_algorithm": "HS256",
            "access_token_expire_minutes": 30,
            "refresh_token_expire_days": 7,
        }

    @pytest.fixture
    def mock_user_repository(self):
        """Mock del repositorio de usuarios."""
        repo = AsyncMock()
        sample_user = User(
            id="123",
            username="john_doe",
            email="john@example.com",
            is_active=True,
            is_verified=True,
            roles=["user"],
            permissions=["read"],
            created_at=datetime.now(),
        )
        repo.get_by_username.return_value = sample_user
        repo.get_by_id.return_value = sample_user
        return repo

    @pytest.fixture
    def mock_password_handler(self):
        """Mock del manejador de contraseñas."""
        handler = Mock()
        handler.verify_password.return_value = True
        handler.hash_password.return_value = "hashed_password"
        return handler

    @pytest.fixture
    def auth_provider(self, auth_config, mock_user_repository, mock_password_handler):
        """Fixture para JWTAuthProvider."""
        from turboapi.security.jwt import JWTAuthProvider

        return JWTAuthProvider(
            config=auth_config,
            user_repository=mock_user_repository,
            password_handler=mock_password_handler,
        )

    @pytest.mark.asyncio
    async def test_authenticate_success(self, auth_provider, mock_user_repository):
        """Prueba autenticación exitosa con credenciales válidas."""
        credentials = {
            "username": "john_doe",
            "password": "correct_password",
        }

        result = await auth_provider.authenticate(credentials)

        assert isinstance(result, AuthResult)
        assert result.success is True
        assert result.user_id == "123"
        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.expires_at is not None
        assert result.error_message is None

    @pytest.mark.asyncio
    async def test_authenticate_failure_invalid_user(self, auth_provider, mock_user_repository):
        """Prueba autenticación fallida con usuario inexistente."""
        mock_user_repository.get_by_username.return_value = None

        credentials = {
            "username": "nonexistent_user",
            "password": "any_password",
        }

        result = await auth_provider.authenticate(credentials)

        assert isinstance(result, AuthResult)
        assert result.success is False
        assert result.user_id is None
        assert result.access_token is None
        assert result.refresh_token is None
        assert result.expires_at is None
        assert result.error_message is not None

    @pytest.mark.asyncio
    async def test_authenticate_failure_wrong_password(self, auth_provider, mock_password_handler):
        """Prueba autenticación fallida con contraseña incorrecta."""
        mock_password_handler.verify_password.return_value = False

        credentials = {
            "username": "john_doe",
            "password": "wrong_password",
        }

        result = await auth_provider.authenticate(credentials)

        assert isinstance(result, AuthResult)
        assert result.success is False
        assert result.user_id is None
        assert result.access_token is None
        assert result.refresh_token is None
        assert result.expires_at is None
        assert result.error_message is not None

    @pytest.mark.asyncio
    async def test_authenticate_failure_inactive_user(self, auth_provider, mock_user_repository):
        """Prueba autenticación fallida con usuario inactivo."""
        inactive_user = User(
            id="123",
            username="john_doe",
            email="john@example.com",
            is_active=False,
            is_verified=True,
            roles=["user"],
            permissions=["read"],
            created_at=datetime.now(),
        )
        mock_user_repository.get_by_username.return_value = inactive_user

        credentials = {
            "username": "john_doe",
            "password": "correct_password",
        }

        result = await auth_provider.authenticate(credentials)

        assert isinstance(result, AuthResult)
        assert result.success is False
        assert result.error_message is not None

    @pytest.mark.asyncio
    async def test_validate_token(self, auth_provider):
        """Prueba validación de tokens."""
        # Primero autenticarse para obtener un token
        credentials = {"username": "john_doe", "password": "correct_password"}
        auth_result = await auth_provider.authenticate(credentials)

        # Validar el token
        payload = await auth_provider.validate_token(auth_result.access_token)

        assert isinstance(payload, TokenPayload)
        assert payload.user_id == "123"
        assert payload.username == "john_doe"

    @pytest.mark.asyncio
    async def test_refresh_token(self, auth_provider):
        """Prueba renovación de tokens."""
        # Primero autenticarse para obtener tokens
        credentials = {"username": "john_doe", "password": "correct_password"}
        auth_result = await auth_provider.authenticate(credentials)

        # Pequeño delay para asegurar timestamps diferentes
        time.sleep(0.1)

        # Renovar token
        refresh_result = await auth_provider.refresh_token(auth_result.refresh_token)

        assert isinstance(refresh_result, AuthResult)
        assert refresh_result.success is True
        assert refresh_result.access_token is not None
        assert refresh_result.refresh_token is not None
        assert refresh_result.access_token != auth_result.access_token  # Nuevo token

    @pytest.mark.asyncio
    async def test_logout(self, auth_provider):
        """Prueba logout (invalidación de token)."""
        # Primero autenticarse
        credentials = {"username": "john_doe", "password": "correct_password"}
        auth_result = await auth_provider.authenticate(credentials)

        # Logout
        logout_result = await auth_provider.logout(auth_result.access_token)

        assert logout_result is True

        # El token debería ser inválido después del logout
        from turboapi.security.exceptions import InvalidTokenError

        with pytest.raises(InvalidTokenError):
            await auth_provider.validate_token(auth_result.access_token)

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, auth_provider, mock_user_repository):
        """Prueba obtención de usuario por ID."""
        user = await auth_provider.get_user_by_id("123")

        assert isinstance(user, User)
        assert user.id == "123"
        assert user.username == "john_doe"

        mock_user_repository.get_by_id.assert_called_once_with("123")


class TestPasswordHandler:
    """Pruebas para el manejador de contraseñas."""

    @pytest.fixture
    def password_handler(self):
        """Fixture para PasswordHandler."""
        from turboapi.security.jwt import PasswordHandler

        return PasswordHandler()

    def test_hash_password(self, password_handler):
        """Prueba hash de contraseñas."""
        password = "my_secret_password"
        hashed = password_handler.hash_password(password)

        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > 50  # bcrypt hash should be long

    def test_verify_password_correct(self, password_handler):
        """Prueba verificación exitosa de contraseña."""
        password = "my_secret_password"
        hashed = password_handler.hash_password(password)

        is_valid = password_handler.verify_password(password, hashed)
        assert is_valid is True

    def test_verify_password_incorrect(self, password_handler):
        """Prueba verificación fallida de contraseña."""
        password = "my_secret_password"
        wrong_password = "wrong_password"
        hashed = password_handler.hash_password(password)

        is_valid = password_handler.verify_password(wrong_password, hashed)
        assert is_valid is False


class TestSecurityExceptions:
    """Pruebas para las excepciones de seguridad."""

    def test_invalid_token_error(self):
        """Prueba la excepción InvalidTokenError."""
        from turboapi.security.exceptions import InvalidTokenError

        error = InvalidTokenError("Token expired")
        assert str(error) == "Token expired"
        assert isinstance(error, Exception)

    def test_authentication_error(self):
        """Prueba la excepción AuthenticationError."""
        from turboapi.security.exceptions import AuthenticationError

        error = AuthenticationError("Invalid credentials")
        assert str(error) == "Invalid credentials"
        assert isinstance(error, Exception)

    def test_authorization_error(self):
        """Prueba la excepción AuthorizationError."""
        from turboapi.security.exceptions import AuthorizationError

        error = AuthorizationError("Access denied")
        assert str(error) == "Access denied"
        assert isinstance(error, Exception)


class TestJWTIntegration:
    """Pruebas de integración para el sistema JWT completo."""

    @pytest.mark.asyncio
    async def test_full_authentication_flow(self):
        """Prueba el flujo completo de autenticación."""
        # Esta prueba simula un flujo real de autenticación
        from unittest.mock import AsyncMock
        from unittest.mock import Mock

        # Setup
        mock_user_repo = AsyncMock()
        mock_password_handler = Mock()

        sample_user = User(
            id="user123",
            username="testuser",
            email="test@example.com",
            is_active=True,
            is_verified=True,
            roles=["user", "premium"],
            permissions=["read", "write"],
            created_at=datetime.now(),
        )

        mock_user_repo.get_by_username.return_value = sample_user
        mock_user_repo.get_by_id.return_value = sample_user
        mock_password_handler.verify_password.return_value = True

        # Crear providers
        from turboapi.security.jwt import JWTAuthProvider

        jwt_config = {
            "jwt_secret": "test_secret_key_very_long_and_secure",
            "jwt_algorithm": "HS256",
            "access_token_expire_minutes": 30,
            "refresh_token_expire_days": 7,
        }

        auth_provider = JWTAuthProvider(
            config=jwt_config,
            user_repository=mock_user_repo,
            password_handler=mock_password_handler,
        )

        # 1. Autenticación inicial
        credentials = {"username": "testuser", "password": "password123"}
        auth_result = await auth_provider.authenticate(credentials)

        assert auth_result.success is True
        assert auth_result.user_id == "user123"
        assert auth_result.access_token is not None
        assert auth_result.refresh_token is not None

        # 2. Validar token obtenido
        token_payload = await auth_provider.validate_token(auth_result.access_token)

        assert token_payload.user_id == "user123"
        assert token_payload.username == "testuser"
        assert "user" in token_payload.roles
        assert "premium" in token_payload.roles
        assert "read" in token_payload.permissions
        assert "write" in token_payload.permissions

        # 3. Renovar token (añadir pequeño delay para asegurar timestamp diferente)
        import time

        time.sleep(0.1)
        refresh_result = await auth_provider.refresh_token(auth_result.refresh_token)

        assert refresh_result.success is True
        assert refresh_result.access_token != auth_result.access_token

        # 4. Logout
        logout_success = await auth_provider.logout(refresh_result.access_token)
        assert logout_success is True
