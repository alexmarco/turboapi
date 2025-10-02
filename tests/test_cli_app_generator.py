"""Pruebas para el generador de aplicaciones."""

import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from turboapi.cli.main import app
from turboapi.cli.templates.app_generator import AppGenerator

runner = CliRunner()


class TestAppGenerator:
    """Pruebas para el AppGenerator."""

    def test_generator_initialization(self) -> None:
        """Prueba la inicialización del generador."""
        generator = AppGenerator()
        assert generator.templates_dir is not None
        assert generator.templates_dir.name == "app_templates"

    def test_create_app_basic(self) -> None:
        """Prueba la creación de una aplicación básica."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = AppGenerator()
            app_name = "test_app"
            target_dir = Path(temp_dir) / "apps"

            generator.create_app(app_name, target_dir)

            app_dir = target_dir / app_name
            assert app_dir.exists()
            assert app_dir.is_dir()

            # Verificar archivos principales
            assert (app_dir / "__init__.py").exists()
            assert (app_dir / "models.py").exists()
            assert (app_dir / "repositories.py").exists()
            assert (app_dir / "controllers.py").exists()
            assert (app_dir / "services.py").exists()
            assert (app_dir / "README.md").exists()

            # Verificar directorio tests
            tests_dir = app_dir / "tests"
            assert tests_dir.exists()
            assert tests_dir.is_dir()
            assert (tests_dir / "__init__.py").exists()
            assert (tests_dir / "test_models.py").exists()

    def test_create_app_with_custom_path(self) -> None:
        """Prueba la creación de una aplicación con ruta personalizada."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = AppGenerator()
            app_name = "custom_app"
            target_dir = Path(temp_dir) / "custom_apps"

            generator.create_app(app_name, target_dir)

            app_dir = target_dir / app_name
            assert app_dir.exists()
            assert app_dir.is_dir()

    def test_create_app_existing_directory(self) -> None:
        """Prueba que falle si el directorio ya existe."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = AppGenerator()
            app_name = "existing_app"
            target_dir = Path(temp_dir) / "apps"

            # Crear el directorio primero
            app_dir = target_dir / app_name
            app_dir.mkdir(parents=True)

            with pytest.raises(Exception, match="ya existe"):
                generator.create_app(app_name, target_dir)

    def test_create_app_default_path(self) -> None:
        """Prueba la creación de una aplicación con ruta por defecto."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            try:
                # Cambiar al directorio temporal
                import os

                os.chdir(temp_dir)

                generator = AppGenerator()
                app_name = "default_app"

                generator.create_app(app_name)

                app_dir = Path("apps") / app_name
                assert app_dir.exists()
                assert app_dir.is_dir()
            finally:
                os.chdir(original_cwd)

    def test_app_structure_content(self) -> None:
        """Prueba que el contenido de los archivos sea correcto."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = AppGenerator()
            app_name = "content_test_app"
            target_dir = Path(temp_dir) / "apps"

            generator.create_app(app_name, target_dir)

            app_dir = target_dir / app_name

            # Verificar contenido de __init__.py
            init_content = (app_dir / "__init__.py").read_text(encoding="utf-8")
            assert f'"""Aplicación {app_name}."""' in init_content

            # Verificar contenido de models.py
            models_content = (app_dir / "models.py").read_text(encoding="utf-8")
            assert "ExampleModel" in models_content
            assert f'__tablename__ = "{app_name}_example"' in models_content

            # Verificar contenido de controllers.py
            controllers_content = (app_dir / "controllers.py").read_text(encoding="utf-8")
            assert "ExampleController" in controllers_content
            assert f'@Controller("/{app_name}")' in controllers_content

            # Verificar contenido de README.md
            readme_content = (app_dir / "README.md").read_text(encoding="utf-8")
            assert f"# {app_name}" in readme_content
            assert f'installed_apps = [\n    "{app_name}",' in readme_content


class TestCLINewApp:
    """Pruebas para el comando CLI new-app."""

    def test_new_app_command_help(self) -> None:
        """Prueba que el comando new-app muestra ayuda correctamente."""
        result = runner.invoke(app, ["new-app", "--help"])

        assert result.exit_code == 0
        assert "Crea una nueva aplicación en el proyecto" in result.output
        assert "app_name" in result.output
        assert "--path" in result.output

    def test_new_app_command_basic(self) -> None:
        """Prueba el comando new-app básico."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            result = runner.invoke(app, ["new-app", "test_app", "--path", str(temp_path)])

            assert result.exit_code == 0
            assert "Creando aplicación 'test_app' en" in result.output
            assert "[OK] Aplicación 'test_app' creada exitosamente" in result.output
            assert (temp_path / "test_app").exists()

    def test_new_app_command_with_custom_path(self) -> None:
        """Prueba el comando new-app con ruta personalizada."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            result = runner.invoke(
                app, ["new-app", "custom_app", "--path", str(temp_path / "custom_apps")]
            )

            assert result.exit_code == 0
            assert "Creando aplicación 'custom_app' en" in result.output
            assert "[OK] Aplicación 'custom_app' creada exitosamente" in result.output
            assert (temp_path / "custom_apps" / "custom_app").exists()

    def test_new_app_command_existing_directory(self) -> None:
        """Prueba el comando new-app con directorio existente."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            # Crear el directorio primero
            (temp_path / "existing_app").mkdir()

            result = runner.invoke(app, ["new-app", "existing_app", "--path", str(temp_path)])

            assert result.exit_code == 1
            assert "[ERROR]" in result.output
            assert "ya existe" in result.output
