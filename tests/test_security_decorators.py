"""Pruebas para los decoradores de seguridad."""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from turboapi.security.exceptions import InvalidTokenError
from turboapi.security.interfaces import TokenPayload
from turboapi.security.interfaces import User


class TestRequireAuthDecorator:
    """Pruebas para el decorador @RequireAuth."""

    @pytest.fixture
    def sample_user(self) -> User:
        """Usuario de prueba."""
        return User(
            id="123",
            username="john_doe",
            email="john@example.com",
            is_active=True,
            is_verified=True,
            roles=["user"],
            permissions=["read"],
            created_at=datetime.now(),
        )

    @pytest.fixture
    def sample_token_payload(self, sample_user) -> TokenPayload:
        """Payload de token de prueba."""
        return TokenPayload(
            user_id=sample_user.id,
            username=sample_user.username,
            roles=sample_user.roles,
            permissions=sample_user.permissions,
            issued_at=datetime.now(),
            expires_at=datetime.now(),
            extra_claims={},
        )

    @pytest.fixture
    def mock_auth_provider(self, sample_user, sample_token_payload):
        """Mock del proveedor de autenticación."""
        auth_provider = AsyncMock()
        auth_provider.validate_token.return_value = sample_token_payload
        auth_provider.get_user_by_id.return_value = sample_user
        return auth_provider

    @pytest.mark.asyncio
    async def test_require_auth_success(self, mock_auth_provider, sample_user):
        """Prueba que @RequireAuth permite acceso con token válido."""
        from turboapi.security.decorators import RequireAuth

        # Crear endpoint protegido
        @RequireAuth()
        async def protected_endpoint(current_user: User) -> dict:
            return {"user_id": current_user.id, "username": current_user.username}

        # Simular request con token válido
        token = "valid_jwt_token"

        # El decorador debería extraer el usuario del token
        result = await protected_endpoint._call_with_auth(token, mock_auth_provider)

        assert result["user_id"] == sample_user.id
        assert result["username"] == sample_user.username
        mock_auth_provider.validate_token.assert_called_once_with(token)

    @pytest.mark.asyncio
    async def test_require_auth_no_token(self):
        """Prueba que @RequireAuth bloquea acceso sin token."""
        from turboapi.security.decorators import RequireAuth

        @RequireAuth()
        async def protected_endpoint(current_user: User) -> dict:
            return {"message": "success"}

        # Sin token debería lanzar HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await protected_endpoint._call_with_auth(None, None)

        assert exc_info.value.status_code == 401
        assert "Missing authorization token" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_require_auth_invalid_token(self, mock_auth_provider):
        """Prueba que @RequireAuth bloquea acceso con token inválido."""
        from turboapi.security.decorators import RequireAuth

        # Configurar mock para lanzar excepción con token inválido
        mock_auth_provider.validate_token.side_effect = InvalidTokenError("Invalid token")

        @RequireAuth()
        async def protected_endpoint(current_user: User) -> dict:
            return {"message": "success"}

        with pytest.raises(HTTPException) as exc_info:
            await protected_endpoint._call_with_auth("invalid_token", mock_auth_provider)

        assert exc_info.value.status_code == 401
        assert "Invalid token" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_require_auth_user_not_found(self, mock_auth_provider, sample_token_payload):
        """Prueba que @RequireAuth bloquea acceso si el usuario no existe."""
        from turboapi.security.decorators import RequireAuth

        # Token válido pero usuario no existe
        mock_auth_provider.validate_token.return_value = sample_token_payload
        mock_auth_provider.get_user_by_id.return_value = None

        @RequireAuth()
        async def protected_endpoint(current_user: User) -> dict:
            return {"message": "success"}

        with pytest.raises(HTTPException) as exc_info:
            await protected_endpoint._call_with_auth("valid_token", mock_auth_provider)

        assert exc_info.value.status_code == 401
        assert "User not found" in str(exc_info.value.detail)


class TestRequireRoleDecorator:
    """Pruebas para el decorador @RequireRole."""

    @pytest.fixture
    def admin_user(self) -> User:
        """Usuario administrador."""
        return User(
            id="admin123",
            username="admin_user",
            email="admin@example.com",
            is_active=True,
            is_verified=True,
            roles=["admin", "user"],
            permissions=["read", "write", "delete"],
            created_at=datetime.now(),
        )

    @pytest.fixture
    def regular_user(self) -> User:
        """Usuario regular."""
        return User(
            id="user123",
            username="regular_user",
            email="user@example.com",
            is_active=True,
            is_verified=True,
            roles=["user"],
            permissions=["read"],
            created_at=datetime.now(),
        )

    @pytest.mark.asyncio
    async def test_require_role_success(self, admin_user):
        """Prueba que @RequireRole permite acceso con el rol correcto."""
        from turboapi.security.decorators import RequireRole

        @RequireRole("admin")
        async def admin_endpoint(current_user: User) -> dict:
            return {"message": "admin access granted", "user": current_user.username}

        result = await admin_endpoint._call_with_user(admin_user)

        assert result["message"] == "admin access granted"
        assert result["user"] == admin_user.username

    @pytest.mark.asyncio
    async def test_require_role_failure(self, regular_user):
        """Prueba que @RequireRole bloquea acceso sin el rol requerido."""
        from turboapi.security.decorators import RequireRole

        @RequireRole("admin")
        async def admin_endpoint(current_user: User) -> dict:
            return {"message": "admin access granted"}

        with pytest.raises(HTTPException) as exc_info:
            await admin_endpoint._call_with_user(regular_user)

        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_require_multiple_roles(self, admin_user, regular_user):
        """Prueba @RequireRole con múltiples roles válidos."""
        from turboapi.security.decorators import RequireRole

        @RequireRole(["admin", "moderator"])
        async def restricted_endpoint(current_user: User) -> dict:
            return {"message": "access granted"}

        # Admin debería tener acceso
        result = await restricted_endpoint._call_with_user(admin_user)
        assert result["message"] == "access granted"

        # Usuario regular no debería tener acceso
        with pytest.raises(HTTPException) as exc_info:
            await restricted_endpoint._call_with_user(regular_user)

        assert exc_info.value.status_code == 403


class TestRequirePermissionDecorator:
    """Pruebas para el decorador @RequirePermission."""

    @pytest.fixture
    def power_user(self) -> User:
        """Usuario con permisos avanzados."""
        return User(
            id="power123",
            username="power_user",
            email="power@example.com",
            is_active=True,
            is_verified=True,
            roles=["editor"],
            permissions=["read", "write", "publish", "user:delete"],
            created_at=datetime.now(),
        )

    @pytest.fixture
    def basic_user(self) -> User:
        """Usuario con permisos básicos."""
        return User(
            id="basic123",
            username="basic_user",
            email="basic@example.com",
            is_active=True,
            is_verified=True,
            roles=["user"],
            permissions=["read"],
            created_at=datetime.now(),
        )

    @pytest.mark.asyncio
    async def test_require_permission_success(self, power_user):
        """Prueba que @RequirePermission permite acceso con el permiso correcto."""
        from turboapi.security.decorators import RequirePermission

        @RequirePermission("write")
        async def write_endpoint(current_user: User) -> dict:
            return {"message": "write access granted", "user": current_user.username}

        result = await write_endpoint._call_with_user(power_user)

        assert result["message"] == "write access granted"
        assert result["user"] == power_user.username

    @pytest.mark.asyncio
    async def test_require_permission_failure(self, basic_user):
        """Prueba que @RequirePermission bloquea acceso sin el permiso requerido."""
        from turboapi.security.decorators import RequirePermission

        @RequirePermission("write")
        async def write_endpoint(current_user: User) -> dict:
            return {"message": "write access granted"}

        with pytest.raises(HTTPException) as exc_info:
            await write_endpoint._call_with_user(basic_user)

        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_require_granular_permission(self, power_user, basic_user):
        """Prueba @RequirePermission con permisos granulares."""
        from turboapi.security.decorators import RequirePermission

        @RequirePermission("user:delete")
        async def delete_user_endpoint(current_user: User) -> dict:
            return {"message": "user deletion allowed"}

        # Power user debería tener acceso
        result = await delete_user_endpoint._call_with_user(power_user)
        assert result["message"] == "user:delete access granted"

        # Basic user no debería tener acceso
        with pytest.raises(HTTPException) as exc_info:
            await delete_user_endpoint._call_with_user(basic_user)

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_require_multiple_permissions(self, power_user, basic_user):
        """Prueba @RequirePermission con múltiples permisos requeridos."""
        from turboapi.security.decorators import RequirePermission

        @RequirePermission(["read", "write", "publish"])
        async def publish_endpoint(current_user: User) -> dict:
            return {"message": "publish access granted"}

        # Power user debería tener acceso (tiene todos los permisos)
        result = await publish_endpoint._call_with_user(power_user)
        assert result["message"] == "access granted"

        # Basic user no debería tener acceso (le falta write y publish)
        with pytest.raises(HTTPException) as exc_info:
            await publish_endpoint._call_with_user(basic_user)

        assert exc_info.value.status_code == 403


class TestCombinedSecurityDecorators:
    """Pruebas para la combinación de decoradores de seguridad."""

    @pytest.fixture
    def super_admin(self) -> User:
        """Usuario super administrador."""
        return User(
            id="super123",
            username="super_admin",
            email="super@example.com",
            is_active=True,
            is_verified=True,
            roles=["admin", "super_admin"],
            permissions=["read", "write", "delete", "admin:manage", "system:access"],
            created_at=datetime.now(),
        )

    @pytest.fixture
    def regular_admin(self) -> User:
        """Usuario administrador regular."""
        return User(
            id="admin123",
            username="admin",
            email="admin@example.com",
            is_active=True,
            is_verified=True,
            roles=["admin"],
            permissions=["read", "write", "delete"],
            created_at=datetime.now(),
        )

    @pytest.mark.asyncio
    async def test_combined_decorators_success(self, super_admin):
        """Prueba combinación exitosa de @RequireRole y @RequirePermission."""
        from turboapi.security.decorators import RequirePermission
        from turboapi.security.decorators import RequireRole

        @RequireRole("super_admin")
        @RequirePermission("system:access")
        async def system_endpoint(current_user: User) -> dict:
            return {"message": "system access granted", "user": current_user.username}

        # Super admin debería pasar ambas validaciones
        result = await system_endpoint._call_with_user(super_admin)

        assert result["message"] == "super_admin access granted"
        assert result["user"] == super_admin.username

    @pytest.mark.asyncio
    async def test_combined_decorators_role_failure(self, regular_admin):
        """Prueba fallo en @RequireRole en decoradores combinados."""
        from turboapi.security.decorators import RequirePermission
        from turboapi.security.decorators import RequireRole

        @RequireRole("super_admin")
        @RequirePermission("delete")
        async def system_endpoint(current_user: User) -> dict:
            return {"message": "system access granted"}

        # Regular admin tiene el permiso pero no el rol
        with pytest.raises(HTTPException) as exc_info:
            await system_endpoint._call_with_user(regular_admin)

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_combined_decorators_permission_failure(self, super_admin):
        """Prueba fallo en @RequirePermission en decoradores combinados."""
        from turboapi.security.decorators import RequirePermission
        from turboapi.security.decorators import RequireRole

        # Crear usuario super_admin sin el permiso específico
        limited_super_admin = User(
            id="limited123",
            username="limited_super",
            email="limited@example.com",
            is_active=True,
            is_verified=True,
            roles=["super_admin"],
            permissions=["read", "write"],  # Sin "special:access"
            created_at=datetime.now(),
        )

        @RequireRole("super_admin")
        @RequirePermission("special:access")
        async def special_endpoint(current_user: User) -> dict:
            return {"message": "special access granted"}

        # Tiene el rol pero no el permiso
        with pytest.raises(HTTPException) as exc_info:
            await special_endpoint._call_with_user(limited_super_admin)

        assert exc_info.value.status_code == 403


class TestSecurityDecoratorIntegration:
    """Pruebas de integración para decoradores con FastAPI."""

    @pytest.mark.asyncio
    async def test_decorator_preserves_function_metadata(self):
        """Prueba que los decoradores preservan metadata de funciones."""
        from turboapi.security.decorators import RequireAuth
        from turboapi.security.decorators import RequirePermission
        from turboapi.security.decorators import RequireRole

        @RequireAuth()
        @RequireRole("admin")
        @RequirePermission("manage")
        async def test_endpoint(current_user: User) -> dict:
            """Test endpoint with security decorators."""
            return {"message": "success"}

        # Verificar que la función mantiene su metadata
        assert test_endpoint.__name__ == "test_endpoint"
        assert "Test endpoint with security decorators" in test_endpoint.__doc__

        # Verificar que los decoradores añaden metadata de seguridad
        assert hasattr(test_endpoint, "_requires_auth")
        assert hasattr(test_endpoint, "_required_roles")
        assert hasattr(test_endpoint, "_required_permissions")

    @pytest.mark.asyncio
    async def test_security_attributes_are_correct(self):
        """Prueba que los decoradores añaden los atributos de seguridad correctos."""
        from turboapi.security.decorators import RequireAuth
        from turboapi.security.decorators import RequirePermission
        from turboapi.security.decorators import RequireRole

        @RequireAuth()
        @RequireRole(["admin", "moderator"])
        @RequirePermission(["read", "write"])
        async def complex_endpoint(current_user: User) -> dict:
            return {"message": "success"}

        assert complex_endpoint._requires_auth is True
        assert "admin" in complex_endpoint._required_roles
        assert "moderator" in complex_endpoint._required_roles
        assert "read" in complex_endpoint._required_permissions
        assert "write" in complex_endpoint._required_permissions
