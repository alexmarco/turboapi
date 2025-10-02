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
from .decorators import RequireAuth, RequirePermission, RequireRole
from .dependencies import (
    get_current_user,
    require_permission,
    require_permissions,
    require_role,
    require_roles,
)
from .jwt import JWTAuthProvider, JWTTokenManager, PasswordHandler
from .middleware import (
    CORSSecurityMiddleware,
    RateLimitMiddleware,
    SecurityMiddleware,
    setup_security_middleware,
)

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
