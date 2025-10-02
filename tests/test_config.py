"""Pruebas para el sistema de configuración del framework."""

from pathlib import Path

import pytest

from turboapi.core.config import ConfigError
from turboapi.core.config import TurboConfig


class TestTurboConfig:
    """Pruebas para el sistema de configuración."""

    def test_load_config_from_pyproject_toml(self, tmp_path: Path) -> None:
        """Prueba que se puede cargar la configuración desde pyproject.toml."""
        # Crear un pyproject.toml de prueba
        pyproject_content = """
[project]
name = "test_project"
version = "0.1.0"

[tool.turboapi]
installed_apps = [
    "apps.home",
    "apps.users",
    "apps.products"
]
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        # Cargar configuración
        config = TurboConfig.from_pyproject(pyproject_file)

        # Verificar que se cargó correctamente
        assert list(config.installed_apps) == ["apps.home", "apps.users", "apps.products"]
        assert config.project_name == "test_project"
        assert config.project_version == "0.1.0"

    def test_load_config_with_empty_installed_apps(self, tmp_path: Path) -> None:
        """Prueba que se puede cargar configuración con installed_apps vacío."""
        pyproject_content = """
[project]
name = "test_project"

[tool.turboapi]
installed_apps = []
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        config = TurboConfig.from_pyproject(pyproject_file)

        assert list(config.installed_apps) == []
        assert config.project_name == "test_project"

    def test_load_config_without_turboapi_section(self, tmp_path: Path) -> None:
        """Prueba que se puede cargar configuración sin sección turboapi."""
        pyproject_content = """
[project]
name = "test_project"
version = "0.1.0"
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        config = TurboConfig.from_pyproject(pyproject_file)

        # Debería usar valores por defecto
        assert list(config.installed_apps) == []
        assert config.project_name == "test_project"

    def test_load_config_without_installed_apps(self, tmp_path: Path) -> None:
        """Prueba que se puede cargar configuración sin installed_apps."""
        pyproject_content = """
[project]
name = "test_project"

[tool.turboapi]
# Sin installed_apps
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        config = TurboConfig.from_pyproject(pyproject_file)

        assert list(config.installed_apps) == []
        assert config.project_name == "test_project"

    def test_load_config_from_nonexistent_file_raises_error(self) -> None:
        """Prueba que cargar desde archivo inexistente lanza error."""
        nonexistent_file = Path("nonexistent.toml")

        with pytest.raises(ConfigError, match="Configuration file not found"):
            TurboConfig.from_pyproject(nonexistent_file)

    def test_load_config_from_invalid_toml_raises_error(self, tmp_path: Path) -> None:
        """Prueba que cargar TOML inválido lanza error."""
        invalid_toml = tmp_path / "invalid.toml"
        invalid_toml.write_text("invalid toml content [[")

        with pytest.raises(ConfigError, match="Invalid TOML configuration"):
            TurboConfig.from_pyproject(invalid_toml)

    def test_config_validation(self, tmp_path: Path) -> None:
        """Prueba que la configuración valida los datos correctamente."""
        # Configuración con installed_apps que no son strings
        pyproject_content = """
[project]
name = "test_project"

[tool.turboapi]
installed_apps = [123, "apps.home"]
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        with pytest.raises(ConfigError, match="All installed_apps must be strings"):
            TurboConfig.from_pyproject(pyproject_file)

    def test_config_immutability(self, tmp_path: Path) -> None:
        """Prueba que la configuración es inmutable."""
        pyproject_content = """
[project]
name = "test_project"

[tool.turboapi]
installed_apps = ["apps.home"]
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        config = TurboConfig.from_pyproject(pyproject_file)

        # Intentar modificar la configuración debería fallar
        with pytest.raises(AttributeError):
            # Intentar modificar una tupla inmutable
            config.installed_apps.append("apps.new")  # type: ignore[attr-defined]

        with pytest.raises(AttributeError):
            # Intentar modificar una propiedad de solo lectura
            config.project_name = "new_name"  # type: ignore[misc]
