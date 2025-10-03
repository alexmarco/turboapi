"""Pruebas para las interfaces de tareas."""

from abc import ABC

import pytest

from turboapi.interfaces import BaseTaskQueue
from turboapi.interfaces import Task
from turboapi.interfaces import TaskStatus


class TestTaskStatus:
    """Pruebas para el enum TaskStatus."""

    def test_task_status_values(self) -> None:
        """Prueba que TaskStatus tiene los valores correctos."""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"


class TestTask:
    """Pruebas para la clase Task."""

    def test_task_creation(self) -> None:
        """Prueba la creación de una tarea."""

        def sample_task() -> str:
            return "Hello"

        task = Task(
            id="task-1",
            name="sample_task",
            func=sample_task,
            args=(),
            kwargs={},
            status=TaskStatus.PENDING,
        )

        assert task.id == "task-1"
        assert task.name == "sample_task"
        assert task.func == sample_task
        assert task.args == ()
        assert task.kwargs == {}
        assert task.status == TaskStatus.PENDING
        assert task.result is None
        assert task.error is None

    def test_task_with_args_and_kwargs(self) -> None:
        """Prueba la creación de una tarea con argumentos."""

        def sample_task(x: int, y: str = "default") -> str:
            return f"{x}-{y}"

        task = Task(
            id="task-2",
            name="sample_task",
            func=sample_task,
            args=(42,),
            kwargs={"y": "test"},
            status=TaskStatus.PENDING,
        )

        assert task.args == (42,)
        assert task.kwargs == {"y": "test"}


class TestBaseTaskQueue:
    """Pruebas para la interfaz BaseTaskQueue."""

    def test_base_task_queue_is_abstract(self) -> None:
        """Prueba que BaseTaskQueue es una clase abstracta."""
        assert issubclass(BaseTaskQueue, ABC)

        with pytest.raises(TypeError):
            BaseTaskQueue()  # type: ignore

    def test_base_task_queue_has_required_methods(self) -> None:
        """Prueba que BaseTaskQueue tiene los métodos requeridos."""
        # Verificar que los métodos abstractos están definidos
        abstract_methods = BaseTaskQueue.__abstractmethods__

        expected_methods = {
            "enqueue",
            "get_task",
            "update_task_status",
            "get_all_tasks",
            "get_task_by_id",
        }

        assert expected_methods.issubset(abstract_methods)

    def test_base_task_queue_method_signatures(self) -> None:
        """Prueba las firmas de los métodos de BaseTaskQueue."""
        # Esto se verificará cuando implementemos una clase concreta
        # Por ahora, solo verificamos que los métodos existen
        assert hasattr(BaseTaskQueue, "enqueue")
        assert hasattr(BaseTaskQueue, "get_task")
        assert hasattr(BaseTaskQueue, "update_task_status")
        assert hasattr(BaseTaskQueue, "get_all_tasks")
        assert hasattr(BaseTaskQueue, "get_task_by_id")
