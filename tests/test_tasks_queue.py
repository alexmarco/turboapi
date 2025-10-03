"""Pruebas para las implementaciones de colas de tareas."""

from turboapi.interfaces import BaseTaskQueue
from turboapi.interfaces import Task
from turboapi.interfaces import TaskStatus
from turboapi.tasks.queue import InMemoryTaskQueue


class TestInMemoryTaskQueue:
    """Pruebas para InMemoryTaskQueue."""

    def test_queue_initialization(self) -> None:
        """Prueba la inicialización de la cola."""
        queue = InMemoryTaskQueue()

        assert isinstance(queue, BaseTaskQueue)
        assert len(queue.get_all_tasks()) == 0

    def test_enqueue_task(self) -> None:
        """Prueba añadir una tarea a la cola."""
        queue = InMemoryTaskQueue()

        def sample_task() -> str:
            return "Hello"

        task = Task(id="task-1", name="sample_task", func=sample_task, status=TaskStatus.PENDING)

        queue.enqueue(task)

        all_tasks = queue.get_all_tasks()
        assert len(all_tasks) == 1
        assert all_tasks[0].id == "task-1"
        assert all_tasks[0].status == TaskStatus.PENDING

    def test_get_task_from_queue(self) -> None:
        """Prueba obtener una tarea de la cola."""
        queue = InMemoryTaskQueue()

        def sample_task() -> str:
            return "Hello"

        task1 = Task(id="task-1", name="sample_task", func=sample_task)
        task2 = Task(id="task-2", name="sample_task", func=sample_task)

        queue.enqueue(task1)
        queue.enqueue(task2)

        # Debe devolver la primera tarea (FIFO)
        next_task = queue.get_task()
        assert next_task is not None
        assert next_task.id == "task-1"

        # La segunda llamada debe devolver la segunda tarea
        next_task = queue.get_task()
        assert next_task is not None
        assert next_task.id == "task-2"

        # No hay más tareas
        next_task = queue.get_task()
        assert next_task is None

    def test_get_task_from_empty_queue(self) -> None:
        """Prueba obtener una tarea de una cola vacía."""
        queue = InMemoryTaskQueue()

        task = queue.get_task()
        assert task is None

    def test_update_task_status(self) -> None:
        """Prueba actualizar el estado de una tarea."""
        queue = InMemoryTaskQueue()

        def sample_task() -> str:
            return "Hello"

        task = Task(id="task-1", name="sample_task", func=sample_task)
        queue.enqueue(task)

        # Actualizar a running
        queue.update_task_status("task-1", TaskStatus.RUNNING)

        updated_task = queue.get_task_by_id("task-1")
        assert updated_task is not None
        assert updated_task.status == TaskStatus.RUNNING
        assert updated_task.started_at is not None

    def test_update_task_status_with_result(self) -> None:
        """Prueba actualizar el estado de una tarea con resultado."""
        queue = InMemoryTaskQueue()

        def sample_task() -> str:
            return "Hello"

        task = Task(id="task-1", name="sample_task", func=sample_task)
        queue.enqueue(task)

        # Actualizar a completed con resultado
        result = "Task completed successfully"
        queue.update_task_status("task-1", TaskStatus.COMPLETED, result=result)

        updated_task = queue.get_task_by_id("task-1")
        assert updated_task is not None
        assert updated_task.status == TaskStatus.COMPLETED
        assert updated_task.result == result
        assert updated_task.completed_at is not None

    def test_update_task_status_with_error(self) -> None:
        """Prueba actualizar el estado de una tarea con error."""
        queue = InMemoryTaskQueue()

        def sample_task() -> str:
            return "Hello"

        task = Task(id="task-1", name="sample_task", func=sample_task)
        queue.enqueue(task)

        # Actualizar a failed con error
        error = "Task failed with exception"
        queue.update_task_status("task-1", TaskStatus.FAILED, error=error)

        updated_task = queue.get_task_by_id("task-1")
        assert updated_task is not None
        assert updated_task.status == TaskStatus.FAILED
        assert updated_task.error == error
        assert updated_task.completed_at is not None

    def test_update_nonexistent_task_status(self) -> None:
        """Prueba actualizar el estado de una tarea que no existe."""
        queue = InMemoryTaskQueue()

        # No debe lanzar excepción, pero tampoco hacer nada
        queue.update_task_status("nonexistent", TaskStatus.COMPLETED)

        assert len(queue.get_all_tasks()) == 0

    def test_get_task_by_id(self) -> None:
        """Prueba obtener una tarea por ID."""
        queue = InMemoryTaskQueue()

        def sample_task() -> str:
            return "Hello"

        task = Task(id="task-1", name="sample_task", func=sample_task)
        queue.enqueue(task)

        found_task = queue.get_task_by_id("task-1")
        assert found_task is not None
        assert found_task.id == "task-1"

        not_found_task = queue.get_task_by_id("nonexistent")
        assert not_found_task is None

    def test_get_all_tasks(self) -> None:
        """Prueba obtener todas las tareas."""
        queue = InMemoryTaskQueue()

        def sample_task() -> str:
            return "Hello"

        task1 = Task(id="task-1", name="sample_task", func=sample_task)
        task2 = Task(id="task-2", name="sample_task", func=sample_task)

        queue.enqueue(task1)
        queue.enqueue(task2)

        all_tasks = queue.get_all_tasks()
        assert len(all_tasks) == 2

        task_ids = [task.id for task in all_tasks]
        assert "task-1" in task_ids
        assert "task-2" in task_ids

    def test_queue_fifo_behavior(self) -> None:
        """Prueba que la cola sigue comportamiento FIFO."""
        queue = InMemoryTaskQueue()

        def sample_task() -> str:
            return "Hello"

        # Añadir tareas en orden
        for i in range(5):
            task = Task(id=f"task-{i}", name="sample_task", func=sample_task)
            queue.enqueue(task)

        # Obtener tareas debe seguir el mismo orden
        for i in range(5):
            task = queue.get_task()
            assert task is not None
            assert task.id == f"task-{i}"

    def test_queue_only_returns_pending_tasks(self) -> None:
        """Prueba que get_task solo devuelve tareas pendientes."""
        queue = InMemoryTaskQueue()

        def sample_task() -> str:
            return "Hello"

        task1 = Task(id="task-1", name="sample_task", func=sample_task, status=TaskStatus.PENDING)
        task2 = Task(id="task-2", name="sample_task", func=sample_task, status=TaskStatus.RUNNING)
        task3 = Task(id="task-3", name="sample_task", func=sample_task, status=TaskStatus.PENDING)

        queue.enqueue(task1)
        queue.enqueue(task2)
        queue.enqueue(task3)

        # Solo debe devolver las tareas pendientes
        next_task = queue.get_task()
        assert next_task is not None
        assert next_task.id == "task-1"

        next_task = queue.get_task()
        assert next_task is not None
        assert next_task.id == "task-3"

        # No hay más tareas pendientes
        next_task = queue.get_task()
        assert next_task is None
