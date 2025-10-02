"""Capa web del framework TurboAPI."""

from .decorators import Controller
from .decorators import Delete
from .decorators import Get
from .decorators import Post
from .decorators import Put
from .routing import TurboAPI
from .types import ControllerMetadata
from .types import ControllerProtocol
from .types import EndpointMetadata
from .types import EndpointProtocol
from .utils import get_controller_metadata
from .utils import get_endpoint_metadata
from .utils import is_controller
from .utils import is_endpoint

__all__ = [
    "Controller",
    "Get",
    "Post",
    "Put",
    "Delete",
    "TurboAPI",
    "ControllerMetadata",
    "ControllerProtocol",
    "EndpointMetadata",
    "EndpointProtocol",
    "get_controller_metadata",
    "get_endpoint_metadata",
    "is_controller",
    "is_endpoint",
]
