"""Pruebas para TaskStarter."""

from pathlib import Path

import pytest

from turboapi.core.application import TurboApplication
from turboapi.core.config import TurboConfig
from turboapi.interfaces import BaseTaskQueue
from turboapi.tasks.queue import InMemoryTaskQueue
from turboapi.tasks.starter import TaskStarter


def create_test_config() -> TurboConfig:
    """Crea una configuración de prueba."""
    return TurboConfig(
        project_name="test_project", project_version="1.0.0", installed_apps=["test_app"]
    )


def create_test_application() -> TurboApplication:
    """Crea una aplicación de prueba."""
    # Crear un archivo pyproject.toml temporal
    import tempfile

    pyproject_content = """[project]
name = "test_project"
version = "1.0.0"

[tool.turboapi]
installed_apps = ["test_app"]
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(pyproject_content)
        pyproject_path = Path(f.name)

    return TurboApplication(pyproject_path)


class TestTaskStarter:
    """Pruebas para TaskStarter."""

    def test_starter_initialization(self) -> None:
        """Prueba la inicialización del starter."""
        application = create_test_application()

        starter = TaskStarter(application)

        assert starter.application == application
        assert starter.queue_implementation == InMemoryTaskQueue

    def test_starter_initialization_with_custom_queue(self) -> None:
        """Prueba la inicialización del starter con cola personalizada."""
        application = create_test_application()

        class CustomQueue(BaseTaskQueue):
            def enqueue(self, task):
                pass

            def get_task(self):
                return None

            def update_task_status(self, task_id, status, result=None, error=None):
                pass

            def get_all_tasks(self):
                return []

            def get_task_by_id(self, task_id):
                return None

        starter = TaskStarter(application, queue_implementation=CustomQueue)

        assert starter.queue_implementation == CustomQueue

    def test_starter_configure(self) -> None:
        """Prueba la configuración del starter."""
        application = create_test_application()

        starter = TaskStarter(application)
        starter.configure()

        # Verificar que la cola se registró como singleton
        queue = application.container.resolve_typed("task_queue", BaseTaskQueue)
        assert queue is not None
        assert isinstance(queue, InMemoryTaskQueue)

    def test_starter_configure_registers_singleton(self) -> None:
        """Prueba que el starter registra la cola como singleton."""
        application = create_test_application()

        starter = TaskStarter(application)
        starter.configure()

        # Obtener la cola dos veces debe devolver la misma instancia
        queue1 = application.container.resolve_typed("task_queue", BaseTaskQueue)
        queue2 = application.container.resolve_typed("task_queue", BaseTaskQueue)

        assert queue1 is queue2

    def test_starter_configure_with_custom_queue(self) -> None:
        """Prueba la configuración del starter con cola personalizada."""
        application = create_test_application()

        class CustomQueue(BaseTaskQueue):
            def enqueue(self, task):
                pass

            def get_task(self):
                return None

            def update_task_status(self, task_id, status, result=None, error=None):
                pass

            def get_all_tasks(self):
                return []

            def get_task_by_id(self, task_id):
                return None

        starter = TaskStarter(application, queue_implementation=CustomQueue)
        starter.configure()

        # Verificar que se registró la cola personalizada
        queue = application.container.resolve_typed("task_queue", BaseTaskQueue)
        assert queue is not None
        assert isinstance(queue, CustomQueue)

    def test_starter_configure_idempotent(self) -> None:
        """Prueba que la configuración del starter es idempotente."""
        application = create_test_application()

        starter = TaskStarter(application)

        # Configurar múltiples veces
        starter.configure()
        queue1 = application.container.resolve_typed("task_queue", BaseTaskQueue)

        starter.configure()
        queue2 = application.container.resolve_typed("task_queue", BaseTaskQueue)

        # Debe ser la misma instancia
        assert queue1 is queue2

    def test_starter_get_queue(self) -> None:
        """Prueba obtener la cola del starter."""
        application = create_test_application()

        starter = TaskStarter(application)
        starter.configure()

        queue = starter.get_queue()
        assert queue is not None
        assert isinstance(queue, InMemoryTaskQueue)

    def test_starter_get_queue_before_configure(self) -> None:
        """Prueba obtener la cola antes de configurar."""
        application = create_test_application()

        starter = TaskStarter(application)

        with pytest.raises(RuntimeError, match="TaskStarter not configured"):
            starter.get_queue()

    def test_starter_is_configured(self) -> None:
        """Prueba el estado de configuración del starter."""
        application = create_test_application()

        starter = TaskStarter(application)

        assert not starter.is_configured()

        starter.configure()

        assert starter.is_configured()
