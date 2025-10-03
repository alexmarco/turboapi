"""Clase base para addons APM."""

from abc import ABC
from abc import abstractmethod
from typing import Any

from turboapi.core.application import TurboApplication
from turboapi.observability.apm import APMConfig
from turboapi.observability.apm import BaseAPMProvider


class BaseAPMAddon(ABC):
    """Clase base para addons APM."""

    def __init__(self, application: TurboApplication, config: dict[str, Any]) -> None:
        """
        Inicializa el addon APM.

        Parameters
        ----------
        application : TurboApplication
            Aplicación TurboAPI.
        config : dict[str, Any]
            Configuración del addon.
        """
        self.application = application
        self.config = config
        self._configured = False

    @abstractmethod
    def create_provider(self, apm_config: APMConfig) -> BaseAPMProvider:
        """
        Crea el proveedor APM.

        Parameters
        ----------
        apm_config : APMConfig
            Configuración APM base.

        Returns
        -------
        BaseAPMProvider
            Proveedor APM creado.
        """
        pass

    def configure(self) -> None:
        """Configura el addon APM."""
        if self._configured:
            return

        if not self.config.get("enabled", False):
            return

        try:
            # Obtener configuración APM base
            apm_config = APMConfig.from_dict(self.config)

            # Crear proveedor
            provider = self.create_provider(apm_config)

            # Obtener APM manager del contenedor
            apm_manager = self.application.container.resolve("apm_manager")

            # Añadir proveedor al manager
            apm_manager.add_provider(provider)

            self._configured = True

        except Exception as e:
            # Log error but don't fail the application
            print(f"Warning: Failed to configure APM addon {self.__class__.__name__}: {e}")

    def is_configured(self) -> bool:
        """
        Verifica si el addon está configurado.

        Returns
        -------
        bool
            True si está configurado, False en caso contrario.
        """
        return self._configured
