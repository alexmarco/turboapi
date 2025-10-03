"""Implementaciones de colas de tareas."""

from collections import deque
from datetime import datetime
from datetime import timezone
from typing import Any

from turboapi.interfaces import BaseTaskQueue
from turboapi.interfaces import Task
from turboapi.interfaces import TaskStatus


class InMemoryTaskQueue(BaseTaskQueue):
    """Implementación en memoria de una cola de tareas."""

    def __init__(self) -> None:
        """Inicializa la cola de tareas."""
        self._tasks: dict[str, Task] = {}
        self._pending_queue: deque[str] = deque()

    def enqueue(self, task: Task) -> None:
        """
        Añade una tarea a la cola.

        Args:
            task: La tarea a añadir.
        """
        self._tasks[task.id] = task
        if task.status == TaskStatus.PENDING:
            self._pending_queue.append(task.id)

    def get_task(self) -> Task | None:
        """
        Obtiene la siguiente tarea pendiente de la cola.

        Returns:
            La siguiente tarea pendiente o None si no hay tareas pendientes.
        """
        while self._pending_queue:
            task_id = self._pending_queue.popleft()
            task = self._tasks.get(task_id)

            if task and task.status == TaskStatus.PENDING:
                return task

        return None

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
        task = self._tasks.get(task_id)
        if not task:
            return

        task.status = status

        current_time = datetime.now(timezone.utc)

        if status == TaskStatus.RUNNING and task.started_at is None:
            task.started_at = current_time
        elif status in (TaskStatus.COMPLETED, TaskStatus.FAILED) and task.completed_at is None:
            task.completed_at = current_time

        if result is not None:
            task.result = result

        if error is not None:
            task.error = error

    def get_all_tasks(self) -> list[Task]:
        """
        Obtiene todas las tareas.

        Returns:
            Lista de todas las tareas.
        """
        return list(self._tasks.values())

    def get_task_by_id(self, task_id: str) -> Task | None:
        """
        Obtiene una tarea por su ID.

        Args:
            task_id: ID de la tarea.

        Returns:
            La tarea o None si no existe.
        """
        return self._tasks.get(task_id)
