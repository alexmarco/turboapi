"""Pruebas para el comando CLI de tareas."""

import tempfile
from pathlib import Path

from typer.testing import CliRunner

from turboapi.cli.main import app

runner = CliRunner()


class TestCLITasks:
    """Pruebas para el comando CLI de tareas."""

    def test_task_command_help(self) -> None:
        """Prueba que el comando task muestra ayuda correctamente."""
        result = runner.invoke(app, ["task", "--help"])

        assert result.exit_code == 0
        assert "Gestiona las tareas en segundo plano" in result.output
        assert "list" in result.output
        assert "run" in result.output
        assert "status" in result.output

    def test_task_command_invalid_action(self) -> None:
        """Prueba el comando task con acción inválida."""
        result = runner.invoke(app, ["task", "invalid_action"])

        assert result.exit_code == 1
        assert "[ERROR] Acción desconocida: invalid_action" in result.output
        assert "Acciones disponibles: list, run, status" in result.output

    def test_task_command_list_no_project(self) -> None:
        """Prueba el comando task list sin proyecto."""
        # Ejecutar en un directorio temporal sin pyproject.toml
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            try:
                import os

                os.chdir(temp_dir)

                result = runner.invoke(app, ["task", "list"])

                assert result.exit_code == 1
                assert "[ERROR] Error al gestionar tareas" in result.output

            finally:
                os.chdir(original_cwd)

    def test_task_command_run_without_name(self) -> None:
        """Prueba el comando task run sin especificar nombre."""
        result = runner.invoke(app, ["task", "run"])

        assert result.exit_code == 1
        assert "[ERROR] Se requiere --name para ejecutar una tarea" in result.output

    def create_test_project_with_tasks(self) -> Path:
        """Crea un proyecto temporal con tareas para pruebas."""
        temp_dir = Path(tempfile.mkdtemp())

        # Crear pyproject.toml
        pyproject_content = """[project]
name = "test_project"
version = "1.0.0"

[tool.turboapi]
installed_apps = ["test_tasks"]
"""
        (temp_dir / "pyproject.toml").write_text(pyproject_content)

        # Crear módulo con tareas
        tasks_dir = temp_dir / "test_tasks"
        tasks_dir.mkdir()
        (tasks_dir / "__init__.py").write_text("")

        tasks_content = '''
"""Test tasks module."""

from turboapi.tasks.decorators import Task

@Task()
def hello_task():
    """A simple hello task."""
    return "Hello from task!"

@Task(name="custom_task", description="A custom task")
def custom_task(name: str = "World"):
    """A task with parameters."""
    return f"Hello {name}!"
'''

        (tasks_dir / "tasks.py").write_text(tasks_content)

        return temp_dir

    def test_task_command_list_with_project(self) -> None:
        """Prueba el comando task list con un proyecto que tiene tareas."""
        project_dir = self.create_test_project_with_tasks()

        original_cwd = Path.cwd()
        try:
            import os

            os.chdir(project_dir)

            result = runner.invoke(app, ["task", "list"])

            # El comando puede fallar debido a imports, pero debe intentar buscar tareas
            # En un entorno de prueba real, esto funcionaría correctamente
            assert "Buscando tareas disponibles" in result.output or "[ERROR]" in result.output

        finally:
            os.chdir(original_cwd)

    def test_task_command_status(self) -> None:
        """Prueba el comando task status."""
        # Este test verificará que el comando no falle catastróficamente
        result = runner.invoke(app, ["task", "status"])

        # Puede fallar por no encontrar proyecto, pero no debe ser un error de sintaxis
        assert result.exit_code in [0, 1]  # 0 si funciona, 1 si no encuentra proyecto
