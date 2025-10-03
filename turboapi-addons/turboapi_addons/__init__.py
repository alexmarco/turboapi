"""TurboAPI Addons - Extensions and integrations for TurboAPI framework."""

__version__ = "0.1.0"
__author__ = "TurboAPI Team"
__email__ = "team@turboapi.dev"

# Import base classes for addon development
from .base import AddonRegistry, AddonStarter, load_addon

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "AddonStarter",
    "AddonRegistry",
    "load_addon",
]
