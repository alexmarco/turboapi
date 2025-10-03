"""Decoradores para la capa web del framework TurboAPI."""

from collections.abc import Callable
from typing import Any


def Controller(
    prefix: str = "",
    tags: list[str] | None = None,
    dependencies: list[Any] | None = None,
) -> Callable[[type], type]:
    """
    Decorador para marcar una clase como controlador de API.

    Args:
        prefix: Prefijo para todas las rutas del controlador
        tags: Etiquetas para agrupar las rutas en la documentación
        dependencies: Dependencias que se aplicarán a todas las rutas

    Returns:
        Decorador que marca la clase como controlador
    """

    def decorator(cls: type[Any]) -> type[Any]:
        # Marcar la clase como controlador
        cls._is_controller = True
        cls._controller_prefix = prefix
        cls._controller_tags = tags or []
        cls._controller_dependencies = dependencies or []

        return cls

    return decorator


def Get(
    path: str = "",
    *,
    response_model: type | None = None,
    status_code: int = 200,
    tags: list[str] | None = None,
    summary: str | None = None,
    description: str | None = None,
    dependencies: list[Any] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorador para marcar un método como endpoint GET.

    Args:
        path: Ruta del endpoint
        response_model: Modelo de respuesta
        status_code: Código de estado HTTP
        tags: Etiquetas para la documentación
        summary: Resumen del endpoint
        description: Descripción del endpoint
        dependencies: Dependencias específicas del endpoint

    Returns:
        Decorador que marca el método como endpoint GET
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # Marcar la función como endpoint
        func._is_endpoint = True  # type: ignore[attr-defined]
        func._http_method = "GET"  # type: ignore[attr-defined]
        func._endpoint_path = path  # type: ignore[attr-defined]
        func._response_model = response_model  # type: ignore[attr-defined]
        func._status_code = status_code  # type: ignore[attr-defined]
        func._endpoint_tags = tags or []  # type: ignore[attr-defined]
        func._endpoint_summary = summary  # type: ignore[attr-defined]
        func._endpoint_description = description  # type: ignore[attr-defined]
        func._endpoint_dependencies = dependencies or []  # type: ignore[attr-defined]

        return func

    return decorator


def Post(
    path: str = "",
    *,
    response_model: type | None = None,
    status_code: int = 201,
    tags: list[str] | None = None,
    summary: str | None = None,
    description: str | None = None,
    dependencies: list[Any] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorador para marcar un método como endpoint POST.

    Args:
        path: Ruta del endpoint
        response_model: Modelo de respuesta
        status_code: Código de estado HTTP
        tags: Etiquetas para la documentación
        summary: Resumen del endpoint
        description: Descripción del endpoint
        dependencies: Dependencias específicas del endpoint

    Returns:
        Decorador que marca el método como endpoint POST
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # Marcar la función como endpoint
        func._is_endpoint = True  # type: ignore[attr-defined]
        func._http_method = "POST"  # type: ignore[attr-defined]
        func._endpoint_path = path  # type: ignore[attr-defined]
        func._response_model = response_model  # type: ignore[attr-defined]
        func._status_code = status_code  # type: ignore[attr-defined]
        func._endpoint_tags = tags or []  # type: ignore[attr-defined]
        func._endpoint_summary = summary  # type: ignore[attr-defined]
        func._endpoint_description = description  # type: ignore[attr-defined]
        func._endpoint_dependencies = dependencies or []  # type: ignore[attr-defined]

        return func

    return decorator


def Put(
    path: str = "",
    *,
    response_model: type | None = None,
    status_code: int = 200,
    tags: list[str] | None = None,
    summary: str | None = None,
    description: str | None = None,
    dependencies: list[Any] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorador para marcar un método como endpoint PUT.

    Args:
        path: Ruta del endpoint
        response_model: Modelo de respuesta
        status_code: Código de estado HTTP
        tags: Etiquetas para la documentación
        summary: Resumen del endpoint
        description: Descripción del endpoint
        dependencies: Dependencias específicas del endpoint

    Returns:
        Decorador que marca el método como endpoint PUT
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # Marcar la función como endpoint
        func._is_endpoint = True  # type: ignore[attr-defined]
        func._http_method = "PUT"  # type: ignore[attr-defined]
        func._endpoint_path = path  # type: ignore[attr-defined]
        func._response_model = response_model  # type: ignore[attr-defined]
        func._status_code = status_code  # type: ignore[attr-defined]
        func._endpoint_tags = tags or []  # type: ignore[attr-defined]
        func._endpoint_summary = summary  # type: ignore[attr-defined]
        func._endpoint_description = description  # type: ignore[attr-defined]
        func._endpoint_dependencies = dependencies or []  # type: ignore[attr-defined]

        return func

    return decorator


def Delete(
    path: str = "",
    *,
    response_model: type | None = None,
    status_code: int = 204,
    tags: list[str] | None = None,
    summary: str | None = None,
    description: str | None = None,
    dependencies: list[Any] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorador para marcar un método como endpoint DELETE.

    Args:
        path: Ruta del endpoint
        response_model: Modelo de respuesta
        status_code: Código de estado HTTP
        tags: Etiquetas para la documentación
        summary: Resumen del endpoint
        description: Descripción del endpoint
        dependencies: Dependencias específicas del endpoint

    Returns:
        Decorador que marca el método como endpoint DELETE
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # Marcar la función como endpoint
        func._is_endpoint = True  # type: ignore[attr-defined]
        func._http_method = "DELETE"  # type: ignore[attr-defined]
        func._endpoint_path = path  # type: ignore[attr-defined]
        func._response_model = response_model  # type: ignore[attr-defined]
        func._status_code = status_code  # type: ignore[attr-defined]
        func._endpoint_tags = tags or []  # type: ignore[attr-defined]
        func._endpoint_summary = summary  # type: ignore[attr-defined]
        func._endpoint_description = description  # type: ignore[attr-defined]
        func._endpoint_dependencies = dependencies or []  # type: ignore[attr-defined]

        return func

    return decorator
