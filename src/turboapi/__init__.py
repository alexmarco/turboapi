"""TurboAPI - Framework de alta productividad sobre FastAPI."""

from .application import TurboAPI
from .application import create_app
from .core.application import TurboApplication
from .core.config import TurboConfig
from .core.di import TurboContainer
from .dependencies import Depends
from .dependencies import TurboHTTPException
from .dependencies import get_current_user
from .dependencies import require_permission
from .dependencies import require_role

__version__ = "0.1.0"

__all__ = [
    # Main API
    "TurboAPI",
    "create_app",
    # Core components
    "TurboApplication",
    "TurboConfig",
    "TurboContainer",
    # Dependencies (abstractions over FastAPI)
    "Depends",
    "get_current_user",
    "require_role",
    "require_permission",
    "TurboHTTPException",
]
