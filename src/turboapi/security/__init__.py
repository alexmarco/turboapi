"""Módulo de seguridad y autenticación de TurboAPI."""

from .decorators import RequireAuth
from .decorators import RequirePermission
from .decorators import RequireRole
from .dependencies import get_current_user
from .dependencies import require_permission
from .dependencies import require_permissions
from .dependencies import require_role
from .dependencies import require_roles
from .exceptions import AuthenticationError
from .exceptions import AuthorizationError
from .exceptions import InvalidTokenError
from .exceptions import SecurityError
from .exceptions import UserInactiveError
from .exceptions import UserNotFoundError
from .interfaces import AuthResult
from .interfaces import BaseAuthProvider
from .interfaces import BaseRBACManager
from .interfaces import BaseTokenManager
from .interfaces import Permission
from .interfaces import Role
from .interfaces import TokenPayload
from .interfaces import User
from .jwt import JWTAuthProvider
from .jwt import JWTTokenManager
from .jwt import PasswordHandler
from .middleware import CORSSecurityMiddleware
from .middleware import RateLimitMiddleware
from .middleware import SecurityMiddleware
from .middleware import setup_security_middleware

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
    # Decorators
    "RequireAuth",
    "RequireRole",
    "RequirePermission",
    # Dependencies
    "get_current_user",
    "require_role",
    "require_roles",
    "require_permission",
    "require_permissions",
    # Middleware
    "SecurityMiddleware",
    "CORSSecurityMiddleware",
    "RateLimitMiddleware",
    "setup_security_middleware",
    # Exceptions
    "SecurityError",
    "InvalidTokenError",
    "AuthenticationError",
    "AuthorizationError",
    "UserNotFoundError",
    "UserInactiveError",
]
