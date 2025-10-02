"""Decoradores para el sistema de tareas."""

import functools
from collections.abc import Callable
from typing import Any
from typing import TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class Task:
    """Decorador para marcar funciones como tareas ejecutables."""

    def __init__(
        self,
        name: str | None = None,
        description: str = "",
        retry_count: int = 0,
        timeout: int | None = None,
    ) -> None:
        """
        Inicializa el decorador de tarea.

        Args:
            name: Nombre personalizado para la tarea. Si no se proporciona, usa el nombre de la
                función.
            description: Descripción de la tarea.
            retry_count: Número de reintentos en caso de fallo.
            timeout: Timeout en segundos para la ejecución de la tarea.
        """
        self.name = name
        self.description = description
        self.retry_count = retry_count
        self.timeout = timeout

    def __call__(self, func: F) -> F:
        """
        Aplica el decorador a la función.

        Args:
            func: La función a decorar.

        Returns:
            La función decorada con metadatos de tarea.
        """
        # Usar el nombre de la función si no se proporciona uno personalizado
        task_name = self.name if self.name is not None else func.__name__

        # Preservar la función original usando functools.wraps
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        # Añadir metadatos de tarea
        wrapper._is_task = True  # type: ignore
        wrapper._task_name = task_name  # type: ignore
        wrapper._task_description = self.description  # type: ignore
        wrapper._task_retry_count = self.retry_count  # type: ignore
        wrapper._task_timeout = self.timeout  # type: ignore

        return wrapper  # type: ignore
