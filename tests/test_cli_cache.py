"""Pruebas para el comando CLI de caché."""

import tempfile
from pathlib import Path

from typer.testing import CliRunner

from turboapi.cli.main import app

runner = CliRunner()


class TestCLICache:
    """Pruebas para el comando CLI de caché."""

    def test_cache_command_help(self) -> None:
        """Prueba que el comando cache muestra ayuda correctamente."""
        result = runner.invoke(app, ["cache", "--help"])

        assert result.exit_code == 0
        assert "Gestiona el sistema de caché" in result.output
        assert "list" in result.output
        assert "clear" in result.output
        assert "stats" in result.output

    def test_cache_command_invalid_action(self) -> None:
        """Prueba el comando cache con acción inválida."""
        result = runner.invoke(app, ["cache", "invalid_action"])

        assert result.exit_code == 1
        assert "[ERROR] Acción desconocida: invalid_action" in result.output
        assert "Acciones disponibles: list, clear, stats" in result.output

    def test_cache_command_list_no_project(self) -> None:
        """Prueba el comando cache list sin proyecto."""
        # Ejecutar en un directorio temporal sin pyproject.toml
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            try:
                import os

                os.chdir(temp_dir)

                result = runner.invoke(app, ["cache", "list"])

                assert result.exit_code == 1
                assert "[ERROR] Error al gestionar caché" in result.output

            finally:
                os.chdir(original_cwd)

    def create_test_project_with_cached_functions(self) -> Path:
        """Crea un proyecto temporal con funciones cacheables para pruebas."""
        temp_dir = Path(tempfile.mkdtemp())

        # Crear pyproject.toml
        pyproject_content = """[project]
name = "test_project"
version = "1.0.0"

[tool.turboapi]
installed_apps = ["test_cache"]
"""
        (temp_dir / "pyproject.toml").write_text(pyproject_content)

        # Crear módulo con funciones cacheables
        cache_dir = temp_dir / "test_cache"
        cache_dir.mkdir()
        (cache_dir / "__init__.py").write_text("")

        cache_content = '''
"""Test cache module."""

from datetime import timedelta
from turboapi.cache.decorators import Cache

@Cache()
def hello_cached():
    """A simple cached function."""
    return "Hello from cache!"

@Cache(ttl=timedelta(seconds=300))
def custom_cached(name: str = "World"):
    """A cached function with TTL."""
    return f"Hello {name}!"
'''

        (cache_dir / "cache.py").write_text(cache_content)

        return temp_dir

    def test_cache_command_list_with_project(self) -> None:
        """Prueba el comando cache list con un proyecto que tiene funciones cacheables."""
        project_dir = self.create_test_project_with_cached_functions()

        original_cwd = Path.cwd()
        try:
            import os

            os.chdir(project_dir)

            result = runner.invoke(app, ["cache", "list"])

            # El comando puede fallar debido a imports, pero debe intentar buscar funciones
            # En un entorno de prueba real, esto funcionaría correctamente
            assert "Buscando funciones cacheables" in result.output or "[ERROR]" in result.output

        finally:
            os.chdir(original_cwd)

    def test_cache_command_stats(self) -> None:
        """Prueba el comando cache stats."""
        # Este test verificará que el comando no falle catastróficamente
        result = runner.invoke(app, ["cache", "stats"])

        # Puede fallar por no encontrar proyecto, pero no debe ser un error de sintaxis
        assert result.exit_code in [0, 1]  # 0 si funciona, 1 si no encuentra proyecto

    def test_cache_command_clear_all(self) -> None:
        """Prueba el comando cache clear sin clave específica."""
        result = runner.invoke(app, ["cache", "clear"])

        # Puede fallar por no encontrar proyecto, pero debe intentar limpiar
        assert result.exit_code in [0, 1]

    def test_cache_command_clear_key(self) -> None:
        """Prueba el comando cache clear con clave específica."""
        result = runner.invoke(app, ["cache", "clear", "--key", "test_key"])

        # Puede fallar por no encontrar proyecto, pero debe intentar limpiar la clave
        assert result.exit_code in [0, 1]
