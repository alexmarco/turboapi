"""Addon APM para New Relic."""

from typing import Any

from turboapi.observability.apm import APMConfig
from turboapi.observability.apm import BaseAPMProvider

from .base import BaseAPMAddon


class NewRelicAPMProvider(BaseAPMProvider):
    """Proveedor APM para New Relic."""

    def __init__(self, config: APMConfig) -> None:
        """
        Inicializa el proveedor New Relic APM.

        Parameters
        ----------
        config : APMConfig
            Configuración del sistema APM.
        """
        super().__init__(config)
        self._newrelic = None

    def initialize(self) -> None:
        """Inicializa el proveedor New Relic APM."""
        if self._initialized:
            return

        try:
            import newrelic.agent

            # Configurar New Relic
            newrelic_config = getattr(self.config, "new_relic", None)
            if newrelic_config:
                newrelic.agent.initialize(
                    config_file=None,
                    environment=self.config.environment,
                    **newrelic_config,
                )

            self._newrelic = newrelic.agent
            self._initialized = True

        except ImportError:
            # New Relic no está instalado
            self._initialized = True

    def start_transaction(self, name: str, transaction_type: str = "web") -> Any:
        """Inicia una transacción New Relic."""
        if not self._initialized or not self._newrelic:
            return None

        return self._newrelic.current_transaction()

    def end_transaction(self, transaction: Any, status: str = "success") -> None:
        """Finaliza una transacción New Relic."""
        if transaction and self._newrelic:
            transaction.add_custom_attribute("status", status)

    def add_custom_attribute(self, transaction: Any, key: str, value: Any) -> None:
        """Añade un atributo personalizado a la transacción."""
        if transaction and self._newrelic:
            transaction.add_custom_attribute(key, value)

    def record_error(self, transaction: Any, error: Exception) -> None:
        """Registra un error en la transacción."""
        if self._newrelic:
            self._newrelic.record_exception(error)

    def record_metric(self, name: str, value: float, tags: dict[str, str] | None = None) -> None:
        """Registra una métrica personalizada."""
        if self._newrelic:
            self._newrelic.record_custom_metric(name, value)


class NewRelicAPMAddon(BaseAPMAddon):
    """Addon APM para New Relic."""

    def create_provider(self, apm_config: APMConfig) -> BaseAPMProvider:
        """
        Crea el proveedor New Relic APM.

        Parameters
        ----------
        apm_config : APMConfig
            Configuración APM base.

        Returns
        -------
        BaseAPMProvider
            Proveedor New Relic APM.
        """
        return NewRelicAPMProvider(apm_config)
