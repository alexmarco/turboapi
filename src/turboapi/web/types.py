"""Tipos para la capa web del framework TurboAPI."""

from collections.abc import Sequence
from typing import Any
from typing import Protocol
from typing import TypedDict


class ControllerProtocol(Protocol):
    """Protocolo que define los atributos que un controlador debe tener."""

    _is_controller: bool
    _controller_prefix: str
    _controller_tags: Sequence[str]
    _controller_dependencies: list[Any]


class EndpointProtocol(Protocol):
    """Protocolo que define los atributos que un endpoint debe tener."""

    _is_endpoint: bool
    _http_method: str
    _endpoint_path: str
    _response_model: type[Any] | None
    _status_code: int
    _endpoint_tags: Sequence[str]
    _endpoint_summary: str | None
    _endpoint_description: str | None
    _endpoint_dependencies: list[Any]


class ControllerMetadata(TypedDict):
    """Metadatos de un controlador."""

    is_controller: bool
    prefix: str
    tags: Sequence[str]
    dependencies: list[Any]


class EndpointMetadata(TypedDict):
    """Metadatos de un endpoint."""

    is_endpoint: bool
    http_method: str
    path: str
    response_model: type[Any] | None
    status_code: int
    tags: Sequence[str]
    summary: str | None
    description: str | None
    dependencies: list[Any]
