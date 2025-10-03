"""Sistema de addons para TurboAPI.

Este módulo proporciona la infraestructura para extender el framework
con funcionalidades adicionales a través de addons/plugins.
"""

from typing import Any
from typing import Protocol

from turboapi.core.application import TurboApplication


class AddonStarter(Protocol):
    """Protocolo para starters de addons."""

    def configure(self) -> None:
        """Configura el addon."""
        ...


class AddonRegistry:
    """Registro de addons disponibles."""

    _addons: dict[str, type[AddonStarter]] = {}

    @classmethod
    def register(cls, name: str, starter_class: type[AddonStarter]) -> None:
        """
        Registra un addon.

        Parameters
        ----------
        name : str
            Nombre del addon.
        starter_class : type[AddonStarter]
            Clase starter del addon.
        """
        cls._addons[name] = starter_class

    @classmethod
    def get_addon(cls, name: str) -> type[AddonStarter] | None:
        """
        Obtiene un addon por nombre.

        Parameters
        ----------
        name : str
            Nombre del addon.

        Returns
        -------
        type[AddonStarter] | None
            Clase starter del addon o None si no existe.
        """
        return cls._addons.get(name)

    @classmethod
    def list_addons(cls) -> list[str]:
        """
        Lista todos los addons registrados.

        Returns
        -------
        list[str]
            Lista de nombres de addons.
        """
        return list(cls._addons.keys())


def load_addon(application: TurboApplication, addon_name: str, config: dict[str, Any]) -> None:
    """
    Carga un addon específico.

    Parameters
    ----------
    application : TurboApplication
        Aplicación TurboAPI.
    addon_name : str
        Nombre del addon a cargar.
    config : dict[str, Any]
        Configuración del addon.
    """
    addon_class = AddonRegistry.get_addon(addon_name)
    if addon_class:
        starter = addon_class(application, config)  # type: ignore[call-arg]
        starter.configure()
    else:
        raise ValueError(f"Addon '{addon_name}' not found")


__all__ = [
    "AddonStarter",
    "AddonRegistry",
    "load_addon",
]
