"""Interfaces y tipos base para TurboAPI."""

from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from enum import Enum
from typing import Any


class TaskStatus(Enum):
    """Estados posibles de una tarea."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """Representa una tarea en el sistema de tareas."""

    id: str
    name: str
    func: Callable[..., Any]
    args: tuple[Any, ...] = field(default_factory=tuple)
    kwargs: dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: datetime | None = None
    completed_at: datetime | None = None


class BaseTaskQueue(ABC):
    """Interfaz base para colas de tareas."""

    @abstractmethod
    def enqueue(self, task: Task) -> None:
        """
        Añade una tarea a la cola.

        Args:
            task: La tarea a añadir.
        """
        pass

    @abstractmethod
    def get_task(self) -> Task | None:
        """
        Obtiene la siguiente tarea de la cola.

        Returns:
            La siguiente tarea o None si la cola está vacía.
        """
        pass

    @abstractmethod
    def update_task_status(
        self, task_id: str, status: TaskStatus, result: Any = None, error: str | None = None
    ) -> None:
        """
        Actualiza el estado de una tarea.

        Args:
            task_id: ID de la tarea.
            status: Nuevo estado.
            result: Resultado de la tarea (si está completada).
            error: Error de la tarea (si falló).
        """
        pass

    @abstractmethod
    def get_all_tasks(self) -> list[Task]:
        """
        Obtiene todas las tareas.

        Returns:
            Lista de todas las tareas.
        """
        pass

    @abstractmethod
    def get_task_by_id(self, task_id: str) -> Task | None:
        """
        Obtiene una tarea por su ID.

        Args:
            task_id: ID de la tarea.

        Returns:
            La tarea o None si no existe.
        """
        pass


class BaseRepository(ABC):
    """Interfaz base para repositorios."""

    @abstractmethod
    def find_by_id(self, entity_id: Any) -> Any:
        """Busca una entidad por ID."""
        pass


@dataclass
class CacheEntry:
    """Representa una entrada en el caché."""

    value: Any
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    access_count: int = 0
    last_accessed: datetime | None = None
    expires_at: datetime | None = None

    def __init__(self, value: Any, ttl: timedelta | None = None) -> None:
        """Inicializa la entrada de caché."""
        self.value = value
        self.created_at = datetime.now(timezone.utc)
        self.access_count = 0
        self.last_accessed = None
        self.expires_at = None

        if ttl is not None:
            self.expires_at = self.created_at + ttl

    def is_expired(self) -> bool:
        """Verifica si la entrada ha expirado."""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    def access(self) -> Any:
        """Accede al valor y actualiza estadísticas."""
        self.access_count += 1
        self.last_accessed = datetime.now(timezone.utc)
        return self.value


class BaseCache(ABC):
    """Interfaz base para sistemas de caché."""

    @abstractmethod
    def get(self, key: str) -> Any:
        """
        Obtiene un valor del caché.

        Args:
            key: Clave del valor.

        Returns:
            El valor almacenado o None si no existe o ha expirado.
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: timedelta | None = None) -> None:
        """
        Almacena un valor en el caché.

        Args:
            key: Clave del valor.
            value: Valor a almacenar.
            ttl: Tiempo de vida del valor.
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Elimina un valor del caché.

        Args:
            key: Clave del valor.

        Returns:
            True si se eliminó, False si no existía.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Limpia todo el caché."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Verifica si una clave existe en el caché.

        Args:
            key: Clave a verificar.

        Returns:
            True si existe y no ha expirado, False en caso contrario.
        """
        pass

    @abstractmethod
    def keys(self) -> list[str]:
        """
        Obtiene todas las claves del caché.

        Returns:
            Lista de claves válidas (no expiradas).
        """
        pass

    @abstractmethod
    def size(self) -> int:
        """
        Obtiene el número de entradas en el caché.

        Returns:
            Número de entradas válidas.
        """
        pass

    @abstractmethod
    def stats(self) -> dict[str, Any]:
        """
        Obtiene estadísticas del caché.

        Returns:
            Diccionario con estadísticas del caché.
        """
        pass


class AsyncBaseCache(ABC):
    """Interfaz base para sistemas de caché asíncronos."""

    @abstractmethod
    async def aget(self, key: str) -> Any:
        """
        Obtiene un valor del caché de forma asíncrona.

        Parameters
        ----------
        key : str
            Clave del valor.

        Returns
        -------
        Any
            El valor almacenado o None si no existe o ha expirado.

        Examples
        --------
        >>> cache = AsyncInMemoryCache()
        >>> await cache.aset("key", "value")
        >>> result = await cache.aget("key")
        >>> print(result)
        'value'
        """
        pass

    @abstractmethod
    async def aset(self, key: str, value: Any, ttl: timedelta | None = None) -> None:
        """
        Almacena un valor en el caché de forma asíncrona.

        Parameters
        ----------
        key : str
            Clave del valor.
        value : Any
            Valor a almacenar.
        ttl : timedelta, optional
            Tiempo de vida del valor.

        Examples
        --------
        >>> cache = AsyncInMemoryCache()
        >>> await cache.aset("key", "value", ttl=timedelta(minutes=5))
        """
        pass

    @abstractmethod
    async def adelete(self, key: str) -> bool:
        """
        Elimina un valor del caché de forma asíncrona.

        Args:
            key: Clave del valor.

        Returns:
            True si se eliminó, False si no existía.
        """
        pass

    @abstractmethod
    async def aclear(self) -> None:
        """Limpia todo el caché de forma asíncrona."""
        pass

    @abstractmethod
    async def aexists(self, key: str) -> bool:
        """
        Verifica si una clave existe en el caché de forma asíncrona.

        Args:
            key: Clave a verificar.

        Returns:
            True si existe y no ha expirado, False en caso contrario.
        """
        pass

    @abstractmethod
    async def akeys(self) -> list[str]:
        """
        Obtiene todas las claves del caché de forma asíncrona.

        Returns:
            Lista de claves válidas (no expiradas).
        """
        pass

    @abstractmethod
    async def asize(self) -> int:
        """
        Obtiene el número de entradas en el caché de forma asíncrona.

        Returns:
            Número de entradas válidas.
        """
        pass

    @abstractmethod
    async def astats(self) -> dict[str, Any]:
        """
        Obtiene estadísticas del caché de forma asíncrona.

        Returns:
            Diccionario con estadísticas del caché.
        """
        pass
