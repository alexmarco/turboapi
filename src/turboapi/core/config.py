"""Sistema de configuración del framework TurboAPI."""

from pathlib import Path

import tomli

from ..exceptions import ConfigError

__all__ = ["TurboConfig", "ConfigError"]


class TurboConfig:
    """Configuración del framework TurboAPI."""

    def __init__(
        self,
        project_name: str,
        project_version: str,
        installed_apps: list[str],
    ) -> None:
        self._project_name = project_name
        self._project_version = project_version
        self._installed_apps = tuple(installed_apps)  # Hacer inmutable

    @property
    def project_name(self) -> str:
        """Nombre del proyecto."""
        return self._project_name

    @property
    def project_version(self) -> str:
        """Versión del proyecto."""
        return self._project_version

    @property
    def installed_apps(self) -> tuple[str, ...]:
        """Lista de aplicaciones instaladas."""
        return self._installed_apps

    @classmethod
    def from_pyproject(cls, pyproject_path: Path) -> "TurboConfig":
        """Carga la configuración desde un archivo pyproject.toml."""
        if not pyproject_path.exists():
            raise ConfigError(reason="Configuration file not found")

        try:
            with open(pyproject_path, "rb") as f:
                data = tomli.load(f)
        except tomli.TOMLDecodeError as e:
            raise ConfigError(reason=f"Invalid TOML configuration: {e}") from e

        # Extraer información del proyecto
        project_data = data.get("project", {})
        project_name = project_data.get("name", "unknown")
        project_version = project_data.get("version", "0.0.0")

        # Extraer configuración de turboapi
        turboapi_data = data.get("tool", {}).get("turboapi", {})
        installed_apps = turboapi_data.get("installed_apps", [])

        # Validar installed_apps
        if not isinstance(installed_apps, list):
            raise ConfigError(reason="installed_apps must be a list")

        for app in installed_apps:
            if not isinstance(app, str):
                raise ConfigError(reason="All installed_apps must be strings")

        return cls(
            project_name=project_name,
            project_version=project_version,
            installed_apps=installed_apps,
        )

    def __repr__(self) -> str:
        """Representación de la configuración."""
        return (
            f"TurboConfig(project_name='{self.project_name}', "
            f"project_version='{self.project_version}', "
            f"installed_apps={list(self.installed_apps)})"
        )
