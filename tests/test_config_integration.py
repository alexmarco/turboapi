"""Pruebas de integración para el sistema de configuración con el contenedor DI."""

from pathlib import Path

from turboapi.core.config import TurboConfig
from turboapi.core.di import ComponentProvider
from turboapi.core.di import TurboContainer


class TestConfigIntegration:
    """Pruebas de integración entre configuración y contenedor DI."""

    def test_register_config_as_singleton(self, tmp_path: Path) -> None:
        """Prueba que se puede registrar la configuración como singleton en el contenedor."""
        # Crear un pyproject.toml de prueba
        pyproject_content = """
[project]
name = "test_project"
version = "0.1.0"

[tool.turboapi]
installed_apps = [
    "apps.home",
    "apps.users"
]
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        # Crear configuración
        config = TurboConfig.from_pyproject(pyproject_file)

        # Crear contenedor y registrar configuración
        container = TurboContainer()
        container.register("config", ComponentProvider(lambda: config, singleton=True))

        # Verificar que se puede resolver la configuración
        resolved_config = container.resolve_typed("config", TurboConfig)

        # Verificar que es la misma instancia (singleton)
        assert resolved_config is config
        assert resolved_config.project_name == "test_project"
        assert list(resolved_config.installed_apps) == ["apps.home", "apps.users"]

    def test_config_singleton_behavior(self, tmp_path: Path) -> None:
        """Prueba que la configuración se comporta como singleton en el contenedor."""
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
        container = TurboContainer()
        container.register("config", ComponentProvider(lambda: config, singleton=True))

        # Resolver múltiples veces
        config1 = container.resolve_typed("config", TurboConfig)
        config2 = container.resolve_typed("config", TurboConfig)

        # Verificar que es la misma instancia
        assert config1 is config2
        assert config1 is config

    def test_config_factory_provider(self, tmp_path: Path) -> None:
        """Prueba que se puede usar un factory provider para la configuración."""
        pyproject_content = """
[project]
name = "test_project"
version = "0.1.0"

[tool.turboapi]
installed_apps = ["apps.home"]
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        container = TurboContainer()

        # Registrar usando un factory que crea la configuración
        def config_factory() -> TurboConfig:
            return TurboConfig.from_pyproject(pyproject_file)

        container.register("config", ComponentProvider(config_factory, singleton=True))

        # Resolver la configuración
        config = container.resolve_typed("config", TurboConfig)

        # Verificar que se creó correctamente
        assert config.project_name == "test_project"
        assert list(config.installed_apps) == ["apps.home"]

        # Verificar que es singleton
        config2 = container.resolve_typed("config", TurboConfig)
        assert config is config2
