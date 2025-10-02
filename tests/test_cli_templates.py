"""Pruebas para las plantillas del CLI."""

import tempfile
from pathlib import Path

import pytest
import typer

from turboapi.cli.templates.generator import ProjectGenerator


class TestProjectGenerator:
    """Pruebas para el generador de proyectos."""

    def test_generator_initialization(self) -> None:
        """Prueba la inicialización del generador."""
        generator = ProjectGenerator()
        assert generator.templates_dir is not None

    def test_create_project_basic_template(self) -> None:
        """Prueba la creación de un proyecto con plantilla básica."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ProjectGenerator()
            target_dir = Path(temp_dir) / "test_project"

            generator.create_project("test_project", "basic", target_dir)

            # Verificar que se creó el directorio
            assert target_dir.exists()
            assert target_dir.is_dir()

            # Verificar estructura de directorios
            assert (target_dir / "apps").exists()
            assert (target_dir / "tests").exists()
            assert (target_dir / "docs").exists()

            # Verificar archivos principales
            assert (target_dir / "pyproject.toml").exists()
            assert (target_dir / "README.md").exists()
            assert (target_dir / "main.py").exists()
            assert (target_dir / ".gitignore").exists()

            # Verificar contenido del pyproject.toml
            with open(target_dir / "pyproject.toml", encoding="utf-8") as f:
                content = f.read()
                assert 'name = "test_project"' in content
                assert "turboapi" in content

    def test_create_project_advanced_template(self) -> None:
        """Prueba la creación de un proyecto con plantilla avanzada."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ProjectGenerator()
            target_dir = Path(temp_dir) / "test_project"

            generator.create_project("test_project", "advanced", target_dir)

            # Verificar estructura básica
            assert target_dir.exists()
            assert (target_dir / "apps").exists()
            assert (target_dir / "tests").exists()
            assert (target_dir / "docs").exists()

            # Verificar estructura avanzada
            assert (target_dir / "config").exists()
            assert (target_dir / "scripts").exists()
            assert (target_dir / "config" / "settings.py").exists()
            assert (target_dir / "config" / "__init__.py").exists()
            assert (target_dir / "scripts" / "start.py").exists()
            assert (target_dir / "scripts" / "__init__.py").exists()

    def test_create_project_invalid_template(self) -> None:
        """Prueba que se lanza error con plantilla inválida."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ProjectGenerator()
            target_dir = Path(temp_dir) / "test_project"

            with pytest.raises(typer.BadParameter, match="Plantilla 'invalid' no reconocida"):
                generator.create_project("test_project", "invalid", target_dir)

    def test_create_project_existing_directory(self) -> None:
        """Prueba que se lanza error si el directorio ya existe."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ProjectGenerator()
            target_dir = Path(temp_dir) / "test_project"

            # Crear el directorio primero
            target_dir.mkdir()

            with pytest.raises(typer.BadParameter, match="ya existe"):
                generator.create_project("test_project", "basic", target_dir)

    def test_create_project_default_path(self) -> None:
        """Prueba la creación de proyecto con ruta por defecto."""
        with tempfile.TemporaryDirectory() as temp_dir:
            import os

            original_cwd = os.getcwd()

            try:
                os.chdir(temp_dir)
                generator = ProjectGenerator()

                generator.create_project("test_project", "basic")

                # Verificar que se creó en el directorio actual
                project_dir = Path(temp_dir) / "test_project"
                assert project_dir.exists()
                assert (project_dir / "pyproject.toml").exists()

            finally:
                os.chdir(original_cwd)

    def test_basic_template_content(self) -> None:
        """Prueba el contenido de la plantilla básica."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ProjectGenerator()
            target_dir = Path(temp_dir) / "test_project"

            generator.create_project("test_project", "basic", target_dir)

            # Verificar contenido del README
            with open(target_dir / "README.md", encoding="utf-8") as f:
                readme_content = f.read()
                assert "# test_project" in readme_content
                assert "Proyecto TurboAPI" in readme_content
                assert "framework run" in readme_content

            # Verificar contenido del main.py
            with open(target_dir / "main.py", encoding="utf-8") as f:
                main_content = f.read()
                assert "from turboapi import TurboAPI" in main_content
                assert "app = TurboAPI()" in main_content
                assert "uvicorn.run" in main_content

            # Verificar contenido del .gitignore
            with open(target_dir / ".gitignore", encoding="utf-8") as f:
                gitignore_content = f.read()
                assert "__pycache__/" in gitignore_content
                assert ".venv" in gitignore_content
                assert "migrations/" in gitignore_content

    def test_advanced_template_content(self) -> None:
        """Prueba el contenido de la plantilla avanzada."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ProjectGenerator()
            target_dir = Path(temp_dir) / "test_project"

            generator.create_project("test_project", "advanced", target_dir)

            # Verificar contenido de config/settings.py
            with open(target_dir / "config" / "settings.py", encoding="utf-8") as f:
                settings_content = f.read()
                assert "from turboapi.core.config import TurboConfig" in settings_content
                assert "config = TurboConfig()" in settings_content

            # Verificar contenido de scripts/start.py
            with open(target_dir / "scripts" / "start.py", encoding="utf-8") as f:
                start_content = f.read()
                assert "import uvicorn" in start_content
                assert "from main import app" in start_content
                assert 'uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)' in start_content
