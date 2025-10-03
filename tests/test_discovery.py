"""Pruebas para el sistema de descubrimiento de componentes."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from turboapi.core.config import TurboConfig
from turboapi.core.discovery import ComponentScanner


class TestComponentScanner:
    """Pruebas para el escáner de componentes."""

    def test_scanner_initialization(self, tmp_path: Path) -> None:
        """Prueba que el escáner se inicializa correctamente."""
        # Crear configuración de prueba
        pyproject_content = """
[project]
name = "test_project"
version = "0.1.0"

[tool.turboapi]
installed_apps = ["apps.home"]
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        config = TurboConfig.from_pyproject(pyproject_file)
        scanner = ComponentScanner(config)

        assert scanner.config is config
        assert scanner._scanned_modules == set()

    def test_scan_empty_installed_apps(self, tmp_path: Path) -> None:
        """Prueba que escanear con installed_apps vacío devuelve lista vacía."""
        pyproject_content = """
[project]
name = "test_project"
version = "0.1.0"

[tool.turboapi]
installed_apps = []
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        config = TurboConfig.from_pyproject(pyproject_file)
        scanner = ComponentScanner(config)

        components = scanner.scan_installed_apps()
        assert components == []

    def test_scan_nonexistent_app_continues_with_others(self, tmp_path: Path) -> None:
        """Prueba que si una app no existe, continúa con las demás."""
        pyproject_content = """
[project]
name = "test_project"
version = "0.1.0"

[tool.turboapi]
installed_apps = ["nonexistent.app", "another.nonexistent"]
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        config = TurboConfig.from_pyproject(pyproject_file)
        scanner = ComponentScanner(config)

        # No debería lanzar excepción, solo imprimir warnings
        components = scanner.scan_installed_apps()
        assert components == []

    def test_scan_module_finds_classes_and_functions(self) -> None:
        """Prueba que el escáner encuentra clases y funciones en un módulo."""

        # Crear un módulo de prueba simple
        class TestModule:
            __name__ = "test_module"
            __file__ = "/path/to/test_module.py"

            class TestClass:
                pass

            @staticmethod
            def test_function() -> None:
                pass

            _private_attr = "should_be_ignored"

        # Crear configuración mock
        config = MagicMock()
        config.installed_apps = ["test_module"]

        scanner = ComponentScanner(config)

        # Mock importlib.import_module para devolver nuestro módulo de prueba
        with pytest.MonkeyPatch().context() as m:
            m.setattr("importlib.import_module", lambda name: TestModule)
            m.setattr("pathlib.Path", lambda path: MagicMock(glob=lambda pattern: []))

            components = scanner.scan_installed_apps()

        # Verificar que encontró las clases y funciones
        assert len(components) >= 2
        assert TestModule.TestClass in components
        assert TestModule.test_function in components

    def test_scan_module_ignores_duplicates(self) -> None:
        """Prueba que el escáner no escanea el mismo módulo dos veces."""

        class TestModule:
            __name__ = "test_module"
            __file__ = "/path/to/test_module.py"

            class TestClass:
                pass

        config = MagicMock()
        config.installed_apps = ["test_module"]

        scanner = ComponentScanner(config)

        with pytest.MonkeyPatch().context() as m:
            m.setattr("importlib.import_module", lambda name: TestModule)
            m.setattr("pathlib.Path", lambda path: MagicMock(glob=lambda pattern: []))

            # Escanear dos veces
            components1 = scanner.scan_installed_apps()
            components2 = scanner.scan_installed_apps()

        # El segundo escaneo debería devolver lista vacía porque ya se escaneó
        assert len(components1) > 0
        assert len(components2) == 0

    def test_find_components_by_type(self) -> None:
        """Prueba que se pueden encontrar componentes por tipo."""

        # Crear módulo de prueba con diferentes tipos
        class TestModule:
            __name__ = "test_module"
            __file__ = "/path/to/test_module.py"

            class TestClass:
                pass

            class AnotherClass:
                pass

            @staticmethod
            def test_function() -> None:
                pass

        config = MagicMock()
        config.installed_apps = ["test_module"]

        scanner = ComponentScanner(config)

        with pytest.MonkeyPatch().context() as m:
            m.setattr("importlib.import_module", lambda name: TestModule)
            m.setattr("pathlib.Path", lambda path: MagicMock(glob=lambda pattern: []))

            # Buscar solo clases
            classes = scanner.find_components_by_type(type)

        # Verificar que encontró las clases correctas
        assert len(classes) >= 2
        assert TestModule.TestClass in classes
        assert TestModule.AnotherClass in classes

    def test_find_components_with_decorator(self) -> None:
        """Prueba que se pueden encontrar componentes con decoradores específicos."""

        # Crear componentes con decoradores simulados
        class TestModule:
            __name__ = "test_module"
            __file__ = "/path/to/test_module.py"

            class DecoratedClass:
                _decorator_name = "Service"

            @staticmethod
            def decorated_function() -> None:
                pass

        # Agregar atributo de decorador a la función
        TestModule.decorated_function._decorator_name = "Controller"  # type: ignore[attr-defined]

        config = MagicMock()
        config.installed_apps = ["test_module"]

        scanner = ComponentScanner(config)

        with pytest.MonkeyPatch().context() as m:
            m.setattr("importlib.import_module", lambda name: TestModule)
            m.setattr("pathlib.Path", lambda path: MagicMock(glob=lambda pattern: []))

            # Buscar componentes con decorador "Service"
            service_components = scanner.find_components_with_decorator("Service")
            controller_components = scanner.find_components_with_decorator("Controller")

        # Verificar que encontró los componentes correctos
        assert len(service_components) >= 1
        assert len(controller_components) >= 1
