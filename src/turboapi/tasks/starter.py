"""Starter para el sistema de tareas."""

from turboapi.core.application import TurboApplication
from turboapi.core.di import ComponentProvider
from turboapi.interfaces import BaseTaskQueue

from .queue import InMemoryTaskQueue


class TaskStarter:
    """Starter para configurar el sistema de tareas."""

    def __init__(
        self,
        application: TurboApplication,
        queue_implementation: type[BaseTaskQueue] = InMemoryTaskQueue,
    ) -> None:
        """
        Inicializa el starter de tareas.

        Args:
            application: La aplicación TurboAPI.
            queue_implementation: Implementación de la cola de tareas a usar.
        """
        self.application = application
        self.queue_implementation = queue_implementation
        self._configured = False

    def configure(self) -> None:
        """Configura el sistema de tareas."""
        if self._configured:
            return

        # Registrar la implementación de la cola como singleton
        self.application.container.register(
            "task_queue", ComponentProvider(lambda: self.queue_implementation(), singleton=True)
        )

        self._configured = True

    def get_queue(self) -> BaseTaskQueue:
        """
        Obtiene la cola de tareas configurada.

        Returns:
            La instancia de la cola de tareas.

        Raises:
            RuntimeError: Si el starter no ha sido configurado.
        """
        if not self._configured:
            raise RuntimeError("TaskStarter not configured. Call configure() first.")

        queue = self.application.container.resolve("task_queue")
        if not isinstance(queue, BaseTaskQueue):
            raise TypeError(f"Expected BaseTaskQueue, got {type(queue)}")
        return queue

    def is_configured(self) -> bool:
        """
        Verifica si el starter ha sido configurado.

        Returns:
            True si está configurado, False en caso contrario.
        """
        return self._configured
