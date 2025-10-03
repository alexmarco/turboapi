"""Pruebas para la aplicación principal del framework."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from turboapi.core.application import TurboApplication
from turboapi.core.config import TurboConfig
from turboapi.core.di import TurboContainer
from turboapi.core.discovery import ComponentScanner


class TestTurboApplication:
    """Pruebas para la aplicación principal del framework."""

    def test_application_initialization(self, tmp_path: Path) -> None:
        """Prueba que la aplicación se inicializa correctamente."""
        # Crear pyproject.toml de prueba
        pyproject_content = """
[project]
name = "test_project"
version = "0.1.0"

[tool.turboapi]
installed_apps = ["apps.home"]
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        app = TurboApplication(pyproject_file)

        # Verificar que se cargó la configuración
        assert app.config.project_name == "test_project"
        assert list(app.config.installed_apps) == ["apps.home"]

        # Verificar que se crearon los componentes
        assert isinstance(app.container, TurboContainer)
        assert isinstance(app.scanner, ComponentScanner)

        # Verificar que no está inicializada aún
        assert not app._initialized

    def test_application_initialize_registers_core_components(self, tmp_path: Path) -> None:
        """Prueba que la inicialización registra los componentes principales."""
        pyproject_content = """
[project]
name = "test_project"
version = "0.1.0"

[tool.turboapi]
installed_apps = []
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        app = TurboApplication(pyproject_file)
        app.initialize()

        # Verificar que se registraron los componentes principales
        assert app.container.is_registered("config")
        assert app.container.is_registered("scanner")
        assert app.container.is_registered("container")

        # Verificar que están marcados como inicializados
        assert app._initialized

    def test_application_initialize_idempotent(self, tmp_path: Path) -> None:
        """Prueba que la inicialización es idempotente."""
        pyproject_content = """
[project]
name = "test_project"
version = "0.1.0"

[tool.turboapi]
installed_apps = []
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        app = TurboApplication(pyproject_file)

        # Inicializar múltiples veces
        app.initialize()
        app.initialize()
        app.initialize()

        # No debería haber errores y debería estar inicializada
        assert app._initialized

    def test_get_component_auto_initializes(self, tmp_path: Path) -> None:
        """Prueba que obtener un componente inicializa automáticamente la aplicación."""
        pyproject_content = """
[project]
name = "test_project"
version = "0.1.0"

[tool.turboapi]
installed_apps = []
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        app = TurboApplication(pyproject_file)

        # Verificar que no está inicializada
        assert not app._initialized

        # Obtener un componente debería inicializar automáticamente
        config = app.get_component("config")

        # Verificar que se inicializó
        assert app._initialized
        assert isinstance(config, TurboConfig)

    def test_get_component_typed(self, tmp_path: Path) -> None:
        """Prueba que se puede obtener un componente con verificación de tipo."""
        pyproject_content = """
[project]
name = "test_project"
version = "0.1.0"

[tool.turboapi]
installed_apps = []
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        app = TurboApplication(pyproject_file)

        # Obtener componentes con verificación de tipo
        config = app.get_component_typed("config", TurboConfig)
        scanner = app.get_component_typed("scanner", ComponentScanner)
        container = app.get_component_typed("container", TurboContainer)

        # Verificar tipos
        assert isinstance(config, TurboConfig)
        assert isinstance(scanner, ComponentScanner)
        assert isinstance(container, TurboContainer)

    def test_get_config(self, tmp_path: Path) -> None:
        """Prueba el método de conveniencia para obtener la configuración."""
        pyproject_content = """
[project]
name = "test_project"
version = "0.1.0"

[tool.turboapi]
installed_apps = ["apps.home", "apps.users"]
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        app = TurboApplication(pyproject_file)
        config = app.get_config()

        assert isinstance(config, TurboConfig)
        assert config.project_name == "test_project"
        assert list(config.installed_apps) == ["apps.home", "apps.users"]

    def test_get_scanner(self, tmp_path: Path) -> None:
        """Prueba el método de conveniencia para obtener el escáner."""
        pyproject_content = """
[project]
name = "test_project"
version = "0.1.0"

[tool.turboapi]
installed_apps = ["apps.home"]
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        app = TurboApplication(pyproject_file)
        scanner = app.get_scanner()

        assert isinstance(scanner, ComponentScanner)
        assert scanner.config is app.config

    def test_get_container(self, tmp_path: Path) -> None:
        """Prueba el método de conveniencia para obtener el contenedor."""
        pyproject_content = """
[project]
name = "test_project"
version = "0.1.0"

[tool.turboapi]
installed_apps = []
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        app = TurboApplication(pyproject_file)
        container = app.get_container()

        assert isinstance(container, TurboContainer)
        assert container is app.container

    def test_register_discovered_components(self, tmp_path: Path) -> None:
        """Prueba que se registran los componentes descubiertos."""

        # Crear un módulo de prueba
        class TestModule:
            __name__ = "test_module"
            __file__ = "/path/to/test_module.py"

            class TestService:
                def __init__(self) -> None:
                    pass

            class TestController:
                def __init__(self) -> None:
                    pass

        pyproject_content = """
[project]
name = "test_project"
version = "0.1.0"

[tool.turboapi]
installed_apps = ["test_module"]
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        app = TurboApplication(pyproject_file)

        # Mock el importlib para devolver nuestro módulo de prueba
        with pytest.MonkeyPatch().context() as m:
            m.setattr("importlib.import_module", lambda name: TestModule)
            m.setattr("pathlib.Path", lambda path: MagicMock(glob=lambda pattern: []))

            app.initialize()

        # Verificar que se registraron los componentes descubiertos
        assert app.container.is_registered("TestService")
        assert app.container.is_registered("TestController")

        # Verificar que se pueden resolver
        service = app.get_component("TestService")
        controller = app.get_component("TestController")

        assert isinstance(service, TestModule.TestService)
        assert isinstance(controller, TestModule.TestController)
