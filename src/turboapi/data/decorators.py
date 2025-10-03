"""Decoradores para la capa de datos del framework TurboAPI."""

from typing import Any


def Repository(
    entity_type: type[Any] | None = None,
    id_type: type[Any] | None = None,
) -> Any:
    """
    Decorador para marcar una clase como repositorio.

    Args:
        entity_type: Tipo de entidad que maneja el repositorio
        id_type: Tipo de ID de la entidad

    Returns:
        Decorador que marca la clase como repositorio
    """

    def decorator(cls: type[Any]) -> type[Any]:
        # Marcar la clase como repositorio
        cls._is_repository = True
        cls._entity_type = entity_type
        cls._id_type = id_type

        return cls

    return decorator
