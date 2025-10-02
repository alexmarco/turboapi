"""Pruebas para el descubrimiento de tareas."""

import sys
import tempfile
from pathlib import Path

from turboapi.core.config import TurboConfig
from turboapi.core.discovery import ComponentScanner


class TestTaskDiscovery:
    """Pruebas para el descubrimiento de tareas."""

    def create_test_module_with_tasks(self) -> tuple[Path, str]:
        """Crea un módulo temporal con tareas para pruebas."""
        # Crear un directorio temporal
        temp_dir = Path(tempfile.mkdtemp())

        # Crear un módulo con tareas
        module_content = '''
"""Test module with tasks."""

from turboapi.tasks.decorators import Task

@Task()
def simple_task():
    """A simple task."""
    return "Hello World"

@Task(name="custom_task", description="A custom task")
def another_task(x: int, y: str = "default"):
    """A task with parameters."""
    return f"{x}-{y}"

@Task(retry_count=3, timeout=60)
def retry_task():
    """A task with retries."""
    return "Retry task"

def not_a_task():
    """This function is not a task."""
    return "Not a task"

class SomeClass:
    """A class that is not a task."""

    @Task()
    def method_task(self):
        """A method that is a task."""
        return "Method task"
'''

        module_file = temp_dir / "test_tasks_module.py"
        module_file.write_text(module_content, encoding="utf-8")

        # Añadir el directorio temporal al path de Python
        sys.path.insert(0, str(temp_dir))

        return temp_dir, "test_tasks_module"

    def test_find_tasks_basic(self) -> None:
        """Prueba el descubrimiento básico de tareas."""
        temp_dir, module_name = self.create_test_module_with_tasks()

        try:
            config = TurboConfig(
                project_name="test_project", project_version="1.0.0", installed_apps=[module_name]
            )

            scanner = ComponentScanner(config)
            tasks = scanner.find_tasks()

            # Debe encontrar las tareas decoradas
            assert len(tasks) >= 3  # Al menos 3 tareas (simple_task, another_task, retry_task)

            # Verificar que son funciones con metadatos de tarea
            task_names = []
            for task_func in tasks:
                assert hasattr(task_func, "_is_task")
                assert task_func._is_task is True
                assert hasattr(task_func, "_task_name")
                task_names.append(task_func._task_name)

            # Verificar que se encontraron las tareas esperadas
            assert "simple_task" in task_names
            assert "custom_task" in task_names  # Nombre personalizado
            assert "retry_task" in task_names

        finally:
            # Limpiar
            sys.path.remove(str(temp_dir))
            if module_name in sys.modules:
                del sys.modules[module_name]

    def test_find_tasks_with_metadata(self) -> None:
        """Prueba que las tareas encontradas mantienen sus metadatos."""
        temp_dir, module_name = self.create_test_module_with_tasks()

        try:
            config = TurboConfig(
                project_name="test_project", project_version="1.0.0", installed_apps=[module_name]
            )

            scanner = ComponentScanner(config)
            tasks = scanner.find_tasks()

            # Buscar la tarea con nombre personalizado
            custom_task = None
            for task_func in tasks:
                if task_func._task_name == "custom_task":
                    custom_task = task_func
                    break

            assert custom_task is not None
            assert custom_task._task_description == "A custom task"

            # Buscar la tarea con reintentos
            retry_task = None
            for task_func in tasks:
                if task_func._task_name == "retry_task":
                    retry_task = task_func
                    break

            assert retry_task is not None
            assert retry_task._task_retry_count == 3
            assert retry_task._task_timeout == 60

        finally:
            # Limpiar
            sys.path.remove(str(temp_dir))
            if module_name in sys.modules:
                del sys.modules[module_name]

    def test_find_tasks_excludes_non_tasks(self) -> None:
        """Prueba que solo se encuentran funciones marcadas como tareas."""
        temp_dir, module_name = self.create_test_module_with_tasks()

        try:
            config = TurboConfig(
                project_name="test_project", project_version="1.0.0", installed_apps=[module_name]
            )

            scanner = ComponentScanner(config)
            tasks = scanner.find_tasks()

            # Verificar que no se incluye la función que no es tarea
            task_names = [task_func._task_name for task_func in tasks]
            assert "not_a_task" not in task_names

        finally:
            # Limpiar
            sys.path.remove(str(temp_dir))
            if module_name in sys.modules:
                del sys.modules[module_name]

    def test_find_tasks_empty_apps(self) -> None:
        """Prueba el descubrimiento de tareas con aplicaciones vacías."""
        config = TurboConfig(
            project_name="test_project", project_version="1.0.0", installed_apps=[]
        )

        scanner = ComponentScanner(config)
        tasks = scanner.find_tasks()

        assert tasks == []

    def test_find_tasks_nonexistent_app(self) -> None:
        """Prueba el descubrimiento de tareas con aplicación inexistente."""
        config = TurboConfig(
            project_name="test_project", project_version="1.0.0", installed_apps=["nonexistent_app"]
        )

        scanner = ComponentScanner(config)
        # No debe lanzar excepción, pero tampoco encontrar tareas
        tasks = scanner.find_tasks()

        assert tasks == []
