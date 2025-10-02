"""Módulo de seguridad y autenticación de TurboAPI."""

from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    InvalidTokenError,
    SecurityError,
    UserInactiveError,
    UserNotFoundError,
)
from .interfaces import (
    AuthResult,
    BaseAuthProvider,
    BaseRBACManager,
    BaseTokenManager,
    Permission,
    Role,
    TokenPayload,
    User,
)
from .jwt import JWTAuthProvider, JWTTokenManager, PasswordHandler

__all__ = [
    # Interfaces
    "BaseAuthProvider",
    "BaseTokenManager",
    "BaseRBACManager",
    "AuthResult",
    "TokenPayload",
    "User",
    "Role",
    "Permission",
    # Implementations
    "JWTAuthProvider",
    "JWTTokenManager",
    "PasswordHandler",
    # Exceptions
    "SecurityError",
    "InvalidTokenError",
    "AuthenticationError",
    "AuthorizationError",
    "UserNotFoundError",
    "UserInactiveError",
]
