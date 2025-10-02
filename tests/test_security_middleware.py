"""Pruebas para el middleware de seguridad de FastAPI."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, Mock
from fastapi import FastAPI, Depends, HTTPException
from fastapi.testclient import TestClient

from turboapi.security.interfaces import User, TokenPayload
from turboapi.security.exceptions import InvalidTokenError


class TestSecurityMiddleware:
    """Pruebas para el middleware de seguridad."""

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

    @pytest.fixture
    def app_with_middleware(self, mock_auth_provider):
        """FastAPI app con middleware de seguridad."""
        from turboapi.security.middleware import SecurityMiddleware
        from turboapi.security.dependencies import get_current_user, get_auth_provider
        
        app = FastAPI()
        
        # Configurar override para el proveedor de autenticación en tests
        def get_mock_auth_provider():
            return mock_auth_provider
        
        app.dependency_overrides[get_auth_provider] = get_mock_auth_provider
        
        # Añadir middleware de seguridad
        app.add_middleware(SecurityMiddleware, auth_provider=mock_auth_provider)
        
        @app.get("/public")
        async def public_endpoint():
            return {"message": "public access"}
        
        @app.get("/protected")
        async def protected_endpoint(current_user: User = Depends(get_current_user)):
            return {"message": "protected access", "user": current_user.username}
        
        return app

    def test_public_endpoint_no_auth_required(self, app_with_middleware):
        """Prueba que endpoints públicos funcionan sin autenticación."""
        with TestClient(app_with_middleware) as client:
            response = client.get("/public")
            
            assert response.status_code == 200
            assert response.json() == {"message": "public access"}

    def test_protected_endpoint_with_valid_token(self, app_with_middleware):
        """Prueba que endpoints protegidos funcionan con token válido."""
        with TestClient(app_with_middleware) as client:
            headers = {"Authorization": "Bearer valid_jwt_token"}
            response = client.get("/protected", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "protected access"
            assert data["user"] == "john_doe"

    def test_protected_endpoint_without_token(self, app_with_middleware):
        """Prueba que endpoints protegidos fallan sin token."""
        with TestClient(app_with_middleware) as client:
            response = client.get("/protected")
            
            assert response.status_code == 401
            assert "Missing authorization token" in response.json()["detail"]

    def test_protected_endpoint_with_invalid_token(self, app_with_middleware, mock_auth_provider):
        """Prueba que endpoints protegidos fallan con token inválido."""
        # Configurar mock para lanzar excepción con token inválido
        mock_auth_provider.validate_token.side_effect = InvalidTokenError("Invalid token")
        
        with TestClient(app_with_middleware) as client:
            headers = {"Authorization": "Bearer invalid_token"}
            response = client.get("/protected", headers=headers)
            
            assert response.status_code == 401
            assert "Invalid token" in response.json()["detail"]

    def test_protected_endpoint_with_bearer_token_format(self, app_with_middleware):
        """Prueba que el middleware maneja correctamente el formato Bearer."""
        with TestClient(app_with_middleware) as client:
            # Test con formato Bearer correcto
            headers = {"Authorization": "Bearer valid_token"}
            response = client.get("/protected", headers=headers)
            assert response.status_code == 200
            
            # Test con formato incorrecto (sin Bearer)
            headers = {"Authorization": "valid_token"}
            response = client.get("/protected", headers=headers)
            assert response.status_code == 401

    def test_middleware_adds_security_headers(self, app_with_middleware):
        """Prueba que el middleware añade headers de seguridad."""
        with TestClient(app_with_middleware) as client:
            response = client.get("/public")
            
            # Verificar headers de seguridad
            assert "X-Content-Type-Options" in response.headers
            assert response.headers["X-Content-Type-Options"] == "nosniff"
            assert "X-Frame-Options" in response.headers
            assert response.headers["X-Frame-Options"] == "DENY"
            assert "X-XSS-Protection" in response.headers
            assert response.headers["X-XSS-Protection"] == "1; mode=block"


class TestSecurityDependencies:
    """Pruebas para las dependencias de seguridad."""

    @pytest.fixture
    def sample_user(self) -> User:
        """Usuario de prueba."""
        return User(
            id="456",
            username="jane_doe",
            email="jane@example.com",
            is_active=True,
            is_verified=True,
            roles=["admin"],
            permissions=["read", "write"],
            created_at=datetime.now(),
        )

    @pytest.fixture
    def mock_auth_provider(self, sample_user):
        """Mock del proveedor de autenticación."""
        auth_provider = AsyncMock()
        
        token_payload = TokenPayload(
            user_id=sample_user.id,
            username=sample_user.username,
            roles=sample_user.roles,
            permissions=sample_user.permissions,
            issued_at=datetime.now(),
            expires_at=datetime.now(),
            extra_claims={},
        )
        
        auth_provider.validate_token.return_value = token_payload
        auth_provider.get_user_by_id.return_value = sample_user
        return auth_provider

    @pytest.mark.asyncio
    async def test_get_current_user_with_valid_token(self, mock_auth_provider, sample_user):
        """Prueba obtener usuario actual con token válido."""
        from turboapi.security.dependencies import get_current_user_impl
        from fastapi import Request
        
        # Simular request con token
        request = Mock(spec=Request)
        request.headers = {"authorization": "Bearer valid_token"}
        
        user = await get_current_user_impl(request, mock_auth_provider)
        
        assert user.id == sample_user.id
        assert user.username == sample_user.username
        assert user.roles == sample_user.roles

    @pytest.mark.asyncio
    async def test_get_current_user_without_token(self, mock_auth_provider):
        """Prueba obtener usuario actual sin token."""
        from turboapi.security.dependencies import get_current_user_impl
        from fastapi import Request
        
        # Simular request sin token
        request = Mock(spec=Request)
        request.headers = {}
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_impl(request, mock_auth_provider)
        
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_with_invalid_token(self, mock_auth_provider):
        """Prueba obtener usuario actual con token inválido."""
        from turboapi.security.dependencies import get_current_user_impl
        from fastapi import Request
        
        # Configurar mock para token inválido
        mock_auth_provider.validate_token.side_effect = InvalidTokenError("Token expired")
        
        request = Mock(spec=Request)
        request.headers = {"authorization": "Bearer expired_token"}
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_impl(request, mock_auth_provider)
        
        assert exc_info.value.status_code == 401
        assert "Token expired" in str(exc_info.value.detail)


class TestRoleBasedDependencies:
    """Pruebas para dependencias basadas en roles."""

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
    async def test_require_admin_role_success(self, admin_user):
        """Prueba dependencia de rol admin con usuario admin."""
        from turboapi.security.dependencies import require_role
        
        admin_dependency = require_role("admin")
        result = await admin_dependency(admin_user)
        
        assert result == admin_user

    @pytest.mark.asyncio
    async def test_require_admin_role_failure(self, regular_user):
        """Prueba dependencia de rol admin con usuario regular."""
        from turboapi.security.dependencies import require_role
        
        admin_dependency = require_role("admin")
        
        with pytest.raises(HTTPException) as exc_info:
            await admin_dependency(regular_user)
        
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_require_permission_success(self, admin_user):
        """Prueba dependencia de permiso con usuario que lo tiene."""
        from turboapi.security.dependencies import require_permission
        
        write_dependency = require_permission("write")
        result = await write_dependency(admin_user)
        
        assert result == admin_user

    @pytest.mark.asyncio
    async def test_require_permission_failure(self, regular_user):
        """Prueba dependencia de permiso con usuario que no lo tiene."""
        from turboapi.security.dependencies import require_permission
        
        write_dependency = require_permission("write")
        
        with pytest.raises(HTTPException) as exc_info:
            await write_dependency(regular_user)
        
        assert exc_info.value.status_code == 403


class TestSecurityIntegration:
    """Pruebas de integración completa del sistema de seguridad."""

    @pytest.fixture
    def complete_app(self):
        """App completa con sistema de seguridad integrado."""
        from turboapi.security.middleware import SecurityMiddleware
        from turboapi.security.dependencies import get_current_user, get_auth_provider, require_role, require_permission
        from turboapi.security.decorators import RequireAuth, RequireRole, RequirePermission
        
        app = FastAPI()
        
        # Mock del proveedor de autenticación
        mock_auth_provider = AsyncMock()
        
        # Usuario admin de prueba
        admin_user = User(
            id="admin123",
            username="admin",
            email="admin@example.com",
            is_active=True,
            is_verified=True,
            roles=["admin"],
            permissions=["read", "write", "delete"],
            created_at=datetime.now(),
        )
        
        token_payload = TokenPayload(
            user_id=admin_user.id,
            username=admin_user.username,
            roles=admin_user.roles,
            permissions=admin_user.permissions,
            issued_at=datetime.now(),
            expires_at=datetime.now(),
            extra_claims={},
        )
        
        mock_auth_provider.validate_token.return_value = token_payload
        mock_auth_provider.get_user_by_id.return_value = admin_user
        
        # Configurar override para el proveedor de autenticación en tests
        def get_mock_auth_provider():
            return mock_auth_provider
        
        app.dependency_overrides[get_auth_provider] = get_mock_auth_provider
        
        # Añadir middleware
        app.add_middleware(SecurityMiddleware, auth_provider=mock_auth_provider)
        
        @app.get("/")
        async def root():
            return {"message": "Welcome to TurboAPI"}
        
        @app.get("/user/profile")
        async def get_profile(current_user: User = Depends(get_current_user)):
            return {"username": current_user.username, "roles": current_user.roles}
        
        @app.get("/admin/users")
        async def list_users(admin_user: User = Depends(require_role("admin"))):
            return {"message": "User list", "admin": admin_user.username}
        
        @app.delete("/admin/users/{user_id}")
        async def delete_user(
            user_id: str,
            admin_user: User = Depends(require_permission("delete"))
        ):
            return {"message": f"User {user_id} deleted", "by": admin_user.username}
        
        # Endpoint con decoradores (para futura integración)
        @app.post("/admin/system")
        @RequireRole("admin")
        @RequirePermission("system:access")
        async def system_action(current_user: User):
            return {"message": "System action executed", "by": current_user.username}
        
        return app

    def test_complete_security_flow(self, complete_app):
        """Prueba el flujo completo de seguridad."""
        with TestClient(complete_app) as client:
            # Endpoint público
            response = client.get("/")
            assert response.status_code == 200
            
            # Endpoint protegido con token válido
            headers = {"Authorization": "Bearer valid_admin_token"}
            
            # Perfil de usuario
            response = client.get("/user/profile", headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert data["username"] == "admin"
            assert "admin" in data["roles"]
            
            # Endpoint de admin
            response = client.get("/admin/users", headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert data["admin"] == "admin"
            
            # Endpoint con permiso específico
            response = client.delete("/admin/users/123", headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert "User 123 deleted" in data["message"]

    def test_security_headers_added(self, complete_app):
        """Prueba que se añaden headers de seguridad."""
        with TestClient(complete_app) as client:
            response = client.get("/")
            
            # Verificar que se añaden headers de seguridad
            security_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options", 
                "X-XSS-Protection",
                "Strict-Transport-Security"
            ]
            
            for header in security_headers:
                assert header in response.headers
