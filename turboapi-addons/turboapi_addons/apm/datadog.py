"""Addon APM para DataDog."""

from typing import Any

from turboapi.observability.apm import APMConfig
from turboapi.observability.apm import BaseAPMProvider

from .base import BaseAPMAddon


class DataDogAPMProvider(BaseAPMProvider):
    """Proveedor APM para DataDog."""

    def __init__(self, config: APMConfig) -> None:
        """
        Inicializa el proveedor DataDog APM.

        Parameters
        ----------
        config : APMConfig
            Configuración del sistema APM.
        """
        super().__init__(config)
        self._ddtrace = None

    def initialize(self) -> None:
        """Inicializa el proveedor DataDog APM."""
        if getattr(self, "_initialized", False):
            return

        try:
            import ddtrace

            # Configurar DataDog
            datadog_config = getattr(self.config, "datadog", None)
            if datadog_config:
                ddtrace.config.service = self.config.service_name
                ddtrace.config.version = self.config.version
                ddtrace.config.env = self.config.environment

                for key, value in datadog_config.items():
                    setattr(ddtrace.config, key, value)

            self._ddtrace = ddtrace
            self._initialized = True

        except ImportError:
            # DataDog no está instalado
            self._initialized = True

    def start_transaction(self, name: str, transaction_type: str = "web") -> Any:
        """Inicia una transacción DataDog."""
        if not self._initialized or not self._ddtrace:
            return None

        return self._ddtrace.tracer.trace(name, service=self.config.service_name)

    def end_transaction(self, transaction: Any, status: str = "success") -> None:
        """Finaliza una transacción DataDog."""
        if transaction:
            transaction.set_tag("status", status)
            transaction.finish()

    def add_custom_attribute(self, transaction: Any, key: str, value: Any) -> None:
        """Añade un atributo personalizado a la transacción."""
        if transaction:
            transaction.set_tag(key, value)

    def record_error(self, transaction: Any, error: Exception) -> None:
        """Registra un error en la transacción."""
        if transaction:
            transaction.set_exc_info(type(error), error, error.__traceback__)

    def record_metric(self, name: str, value: float, tags: dict[str, str] | None = None) -> None:
        """Registra una métrica personalizada."""
        if self._ddtrace:
            self._ddtrace.statsd.increment(name, value, tags=tags or [])


class DataDogAPMAddon(BaseAPMAddon):
    """Addon APM para DataDog."""

    def create_provider(self, apm_config: APMConfig) -> BaseAPMProvider:
        """
        Crea el proveedor DataDog APM.

        Parameters
        ----------
        apm_config : APMConfig
            Configuración APM base.

        Returns
        -------
        BaseAPMProvider
            Proveedor DataDog APM.
        """
        return DataDogAPMProvider(apm_config)
