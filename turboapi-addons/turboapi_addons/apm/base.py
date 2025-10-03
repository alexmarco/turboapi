"""Base class for APM addons."""

from abc import ABC, abstractmethod
from typing import Any

from turboapi.core.application import TurboApplication
from turboapi.observability.apm import APMConfig, BaseAPMProvider


class BaseAPMAddon(ABC):
    """Base class for APM addons."""

    def __init__(self, application: TurboApplication, config: dict[str, Any]) -> None:
        """
        Initialize APM addon.

        Parameters
        ----------
        application : TurboApplication
            TurboAPI application.
        config : dict[str, Any]
            Addon configuration.
        """
        self.application = application
        self.config = config
        self._configured = False

    @abstractmethod
    def create_provider(self, apm_config: APMConfig) -> BaseAPMProvider:
        """
        Create APM provider.

        Parameters
        ----------
        apm_config : APMConfig
            Base APM configuration.

        Returns
        -------
        BaseAPMProvider
            Created APM provider.
        """
        pass

    def configure(self) -> None:
        """Configure APM addon."""
        if self._configured:
            return

        if not self.config.get("enabled", False):
            return

        try:
            # Get base APM configuration
            apm_config = APMConfig.from_dict(self.config)

            # Create provider
            provider = self.create_provider(apm_config)

            # Get APM manager from container
            apm_manager = self.application.container.resolve("apm_manager")

            # Add provider to manager
            apm_manager.add_provider(provider)

            self._configured = True

        except Exception as e:
            # Log error but don't fail the application
            print(f"Warning: Failed to configure APM addon {self.__class__.__name__}: {e}")

    def is_configured(self) -> bool:
        """
        Check if addon is configured.

        Returns
        -------
        bool
            True if configured, False otherwise.
        """
        return self._configured
