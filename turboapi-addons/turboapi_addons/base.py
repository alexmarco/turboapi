"""Base classes for TurboAPI addons.

This module provides the infrastructure for extending the framework
with additional functionality through addons/plugins.
"""

from typing import Any, Protocol

from turboapi.core.application import TurboApplication


class AddonStarter(Protocol):
    """Protocol for addon starters."""

    def configure(self) -> None:
        """Configure the addon."""
        ...


class AddonRegistry:
    """Registry of available addons."""

    _addons: dict[str, type[AddonStarter]] = {}

    @classmethod
    def register(cls, name: str, starter_class: type[AddonStarter]) -> None:
        """
        Register an addon.

        Parameters
        ----------
        name : str
            Addon name.
        starter_class : type[AddonStarter]
            Addon starter class.
        """
        cls._addons[name] = starter_class

    @classmethod
    def get_addon(cls, name: str) -> type[AddonStarter] | None:
        """
        Get an addon by name.

        Parameters
        ----------
        name : str
            Addon name.

        Returns
        -------
        type[AddonStarter] | None
            Addon starter class or None if not found.
        """
        return cls._addons.get(name)

    @classmethod
    def list_addons(cls) -> list[str]:
        """
        List all registered addons.

        Returns
        -------
        list[str]
            List of addon names.
        """
        return list(cls._addons.keys())


def load_addon(application: TurboApplication, addon_name: str, config: dict[str, Any]) -> None:
    """
    Load a specific addon.

    Parameters
    ----------
    application : TurboApplication
        TurboAPI application.
    addon_name : str
        Addon name to load.
    config : dict[str, Any]
        Addon configuration.
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
