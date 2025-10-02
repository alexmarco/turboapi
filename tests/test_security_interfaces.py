"""Pruebas para las interfaces del sistema de seguridad."""

import pytest
from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from turboapi.security.interfaces import (
    BaseAuthProvider,
    BaseTokenManager,
    BaseRBACManager,
    AuthResult,
    TokenPayload,
    User,
    Role,
    Permission,
)


class TestSecurityInterfaces:
    """Pruebas para verificar que las interfaces de seguridad están correctamente definidas."""

    def test_auth_result_dataclass(self) -> None:
        """Prueba que AuthResult es un dataclass válido."""
        result = AuthResult(
            success=True,
            user_id="123",
            access_token="jwt_token",
            refresh_token="refresh_token",
            expires_at=datetime.now() + timedelta(hours=1),
            error_message=None
        )
        
        assert result.success is True
        assert result.user_id == "123"
        assert result.access_token == "jwt_token"
        assert result.refresh_token == "refresh_token"
        assert result.error_message is None
        assert isinstance(result.expires_at, datetime)

    def test_auth_result_failure(self) -> None:
        """Prueba AuthResult para casos de fallo de autenticación."""
        result = AuthResult(
            success=False,
            user_id=None,
            access_token=None,
            refresh_token=None,
            expires_at=None,
            error_message="Invalid credentials"
        )
        
        assert result.success is False
        assert result.user_id is None
        assert result.access_token is None
        assert result.refresh_token is None
        assert result.expires_at is None
        assert result.error_message == "Invalid credentials"

    def test_token_payload_dataclass(self) -> None:
        """Prueba que TokenPayload es un dataclass válido."""
        payload = TokenPayload(
            user_id="123",
            username="john_doe",
            roles=["user", "admin"],
            permissions=["read", "write"],
            issued_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1),
            extra_claims={"department": "engineering"}
        )
        
        assert payload.user_id == "123"
        assert payload.username == "john_doe"
        assert payload.roles == ["user", "admin"]
        assert payload.permissions == ["read", "write"]
        assert isinstance(payload.issued_at, datetime)
        assert isinstance(payload.expires_at, datetime)
        assert payload.extra_claims == {"department": "engineering"}

    def test_user_dataclass(self) -> None:
        """Prueba que User es un dataclass válido."""
        user = User(
            id="123",
            username="john_doe",
            email="john@example.com",
            is_active=True,
            is_verified=True,
            roles=["user"],
            permissions=["read"],
            created_at=datetime.now(),
            last_login=None,
            extra_data={"full_name": "John Doe"}
        )
        
        assert user.id == "123"
        assert user.username == "john_doe"
        assert user.email == "john@example.com"
        assert user.is_active is True
        assert user.is_verified is True
        assert user.roles == ["user"]
        assert user.permissions == ["read"]
        assert isinstance(user.created_at, datetime)
        assert user.last_login is None
        assert user.extra_data == {"full_name": "John Doe"}

    def test_role_dataclass(self) -> None:
        """Prueba que Role es un dataclass válido."""
        role = Role(
            name="admin",
            description="Administrator role",
            permissions=["read", "write", "delete"],
            is_system_role=True,
            created_at=datetime.now()
        )
        
        assert role.name == "admin"
        assert role.description == "Administrator role"
        assert role.permissions == ["read", "write", "delete"]
        assert role.is_system_role is True
        assert isinstance(role.created_at, datetime)

    def test_permission_dataclass(self) -> None:
        """Prueba que Permission es un dataclass válido."""
        permission = Permission(
            name="user:read",
            description="Read user data",
            resource="user",
            action="read",
            created_at=datetime.now()
        )
        
        assert permission.name == "user:read"
        assert permission.description == "Read user data"
        assert permission.resource == "user"
        assert permission.action == "read"
        assert isinstance(permission.created_at, datetime)

    def test_base_auth_provider_is_abstract(self) -> None:
        """Prueba que BaseAuthProvider es una clase abstracta."""
        assert issubclass(BaseAuthProvider, ABC)
        
        # Verificar que no se puede instanciar directamente
        with pytest.raises(TypeError):
            BaseAuthProvider()  # type: ignore

    def test_base_auth_provider_has_required_methods(self) -> None:
        """Prueba que BaseAuthProvider tiene los métodos requeridos."""
        required_methods = {
            "authenticate",
            "validate_token",
            "refresh_token",
            "logout",
            "get_user_by_id",
        }
        
        actual_methods = {
            name for name, method in BaseAuthProvider.__dict__.items()
            if callable(method) and not name.startswith('_')
        }
        
        assert required_methods.issubset(actual_methods)

    def test_base_token_manager_is_abstract(self) -> None:
        """Prueba que BaseTokenManager es una clase abstracta."""
        assert issubclass(BaseTokenManager, ABC)
        
        # Verificar que no se puede instanciar directamente
        with pytest.raises(TypeError):
            BaseTokenManager()  # type: ignore

    def test_base_token_manager_has_required_methods(self) -> None:
        """Prueba que BaseTokenManager tiene los métodos requeridos."""
        required_methods = {
            "generate_access_token",
            "generate_refresh_token",
            "verify_access_token",
            "verify_refresh_token",
            "revoke_token",
        }
        
        actual_methods = {
            name for name, method in BaseTokenManager.__dict__.items()
            if callable(method) and not name.startswith('_')
        }
        
        assert required_methods.issubset(actual_methods)

    def test_base_rbac_manager_is_abstract(self) -> None:
        """Prueba que BaseRBACManager es una clase abstracta."""
        assert issubclass(BaseRBACManager, ABC)
        
        # Verificar que no se puede instanciar directamente
        with pytest.raises(TypeError):
            BaseRBACManager()  # type: ignore

    def test_base_rbac_manager_has_required_methods(self) -> None:
        """Prueba que BaseRBACManager tiene los métodos requeridos."""
        required_methods = {
            "check_permission",
            "check_role",
            "assign_role",
            "revoke_role",
            "create_role",
            "create_permission",
            "get_user_roles",
            "get_user_permissions",
        }
        
        actual_methods = {
            name for name, method in BaseRBACManager.__dict__.items()
            if callable(method) and not name.startswith('_')
        }
        
        assert required_methods.issubset(actual_methods)


class TestSecurityInterfacesIntegration:
    """Pruebas de integración entre las interfaces de seguridad."""

    def test_auth_result_with_token_payload(self) -> None:
        """Prueba la integración entre AuthResult y TokenPayload."""
        now = datetime.now()
        expires = now + timedelta(hours=1)
        
        # Simular flujo de autenticación exitosa
        auth_result = AuthResult(
            success=True,
            user_id="123",
            access_token="jwt_token_here",
            refresh_token="refresh_token_here",
            expires_at=expires,
            error_message=None
        )
        
        # TokenPayload que se extraería del token
        token_payload = TokenPayload(
            user_id=auth_result.user_id,
            username="john_doe",
            roles=["user"],
            permissions=["read"],
            issued_at=now,
            expires_at=auth_result.expires_at,
            extra_claims={}
        )
        
        assert auth_result.user_id == token_payload.user_id
        assert auth_result.expires_at == token_payload.expires_at

    def test_user_with_role_and_permissions(self) -> None:
        """Prueba la integración entre User, Role y Permission."""
        # Crear permisos
        read_perm = Permission(
            name="user:read",
            description="Read user data",
            resource="user",
            action="read",
            created_at=datetime.now()
        )
        
        write_perm = Permission(
            name="user:write",
            description="Write user data",
            resource="user",
            action="write",
            created_at=datetime.now()
        )
        
        # Crear rol
        user_role = Role(
            name="user",
            description="Standard user role",
            permissions=[read_perm.name, write_perm.name],
            is_system_role=False,
            created_at=datetime.now()
        )
        
        # Crear usuario
        user = User(
            id="123",
            username="john_doe",
            email="john@example.com",
            is_active=True,
            is_verified=True,
            roles=[user_role.name],
            permissions=user_role.permissions,
            created_at=datetime.now(),
            last_login=None,
            extra_data={}
        )
        
        assert user_role.name in user.roles
        assert read_perm.name in user.permissions
        assert write_perm.name in user.permissions
