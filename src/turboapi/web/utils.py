"""Utilidades para la capa web del framework TurboAPI."""

from typing import Any
from typing import cast

from .types import ControllerMetadata
from .types import ControllerProtocol
from .types import EndpointMetadata
from .types import EndpointProtocol


def get_controller_metadata(controller_class: type[Any]) -> ControllerMetadata:
    """
    Obtiene los metadatos de un controlador de manera type-safe.

    Args:
        controller_class: Clase del controlador

    Returns:
        Metadatos del controlador
    """
    controller = cast(ControllerProtocol, controller_class)

    return ControllerMetadata(
        is_controller=getattr(controller, "_is_controller", False),
        prefix=getattr(controller, "_controller_prefix", ""),
        tags=getattr(controller, "_controller_tags", []),
        dependencies=getattr(controller, "_controller_dependencies", []),
    )


def get_endpoint_metadata(endpoint_func: Any) -> EndpointMetadata:
    """
    Obtiene los metadatos de un endpoint de manera type-safe.

    Args:
        endpoint_func: Función del endpoint

    Returns:
        Metadatos del endpoint
    """
    endpoint = cast(EndpointProtocol, endpoint_func)

    return EndpointMetadata(
        is_endpoint=getattr(endpoint, "_is_endpoint", False),
        http_method=getattr(endpoint, "_http_method", "GET"),
        path=getattr(endpoint, "_endpoint_path", ""),
        response_model=getattr(endpoint, "_response_model", None),
        status_code=getattr(endpoint, "_status_code", 200),
        tags=getattr(endpoint, "_endpoint_tags", []),
        summary=getattr(endpoint, "_endpoint_summary", None),
        description=getattr(endpoint, "_endpoint_description", None),
        dependencies=getattr(endpoint, "_endpoint_dependencies", []),
    )


def is_controller(controller_class: type[Any]) -> bool:
    """
    Verifica si una clase es un controlador de manera type-safe.

    Args:
        controller_class: Clase a verificar

    Returns:
        True si es un controlador, False en caso contrario
    """
    return getattr(controller_class, "_is_controller", False)


def is_endpoint(endpoint_func: Any) -> bool:
    """
    Verifica si una función es un endpoint de manera type-safe.

    Args:
        endpoint_func: Función a verificar

    Returns:
        True si es un endpoint, False en caso contrario
    """
    return getattr(endpoint_func, "_is_endpoint", False)
