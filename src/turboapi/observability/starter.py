"""Starter para el sistema de observabilidad."""

from typing import Any

from turboapi.core.application import TurboApplication
from turboapi.core.di import ComponentProvider
from turboapi.observability.apm import APMConfig
from turboapi.observability.apm import configure_apm
from turboapi.observability.health import HealthChecker
from turboapi.observability.logging import LoggingConfig
from turboapi.observability.logging import TurboLogging
from turboapi.observability.metrics import MetricConfig
from turboapi.observability.metrics import OpenTelemetryCollector
from turboapi.observability.tracing import OpenTelemetryTracer
from turboapi.observability.tracing import TracingConfig


class ObservabilityStarter:
    """Starter para configurar el sistema de observabilidad."""

    def __init__(
        self,
        application: TurboApplication,
        apm_config: dict[str, Any] | None = None,
        logging_config: dict[str, Any] | None = None,
        metrics_config: dict[str, Any] | None = None,
        tracing_config: dict[str, Any] | None = None,
        health_config: dict[str, Any] | None = None,
    ) -> None:
        """
        Inicializa el starter de observabilidad.

        Args:
            application: La aplicación TurboAPI.
            apm_config: Configuración APM (opcional).
            logging_config: Configuración de logging (opcional).
            metrics_config: Configuración de métricas (opcional).
            tracing_config: Configuración de tracing (opcional).
            health_config: Configuración de health checks (opcional).
        """
        self.application = application
        self.apm_config = apm_config or {}
        self.logging_config = logging_config or {}
        self.metrics_config = metrics_config or {}
        self.tracing_config = tracing_config or {}
        self.health_config = health_config or {}
        self._configured = False

    def configure(self) -> None:
        """Configura el sistema de observabilidad."""
        if self._configured:
            return

        # Configurar logging
        self._configure_logging()

        # Configurar métricas
        self._configure_metrics()

        # Configurar tracing
        self._configure_tracing()

        # Configurar APM
        self._configure_apm()

        # Configurar health checks
        self._configure_health()

        self._configured = True

    def _configure_logging(self) -> None:
        """Configura el sistema de logging."""
        if not self.logging_config.get("enabled", True):
            return

        logging_config = LoggingConfig.from_dict(self.logging_config)
        logging = TurboLogging(logging_config)

        # Registrar en el contenedor DI
        self.application.container.register(
            "logging", ComponentProvider(lambda: logging, singleton=True)
        )

    def _configure_metrics(self) -> None:
        """Configura el sistema de métricas."""
        if not self.metrics_config.get("enabled", True):
            return

        metrics_config = MetricConfig.from_dict(self.metrics_config)
        collector = OpenTelemetryCollector(metrics_config)

        # Registrar en el contenedor DI
        self.application.container.register(
            "metrics_collector", ComponentProvider(lambda: collector, singleton=True)
        )

    def _configure_tracing(self) -> None:
        """Configura el sistema de tracing."""
        if not self.tracing_config.get("enabled", True):
            return

        tracing_config = TracingConfig.from_dict(self.tracing_config)
        tracer = OpenTelemetryTracer(tracing_config)

        # Registrar en el contenedor DI
        self.application.container.register(
            "tracer", ComponentProvider(lambda: tracer, singleton=True)
        )

    def _configure_apm(self) -> None:
        """Configura el sistema APM."""
        if not self.apm_config.get("enabled", True):
            return

        # Crear configuración APM
        apm_config = APMConfig.from_dict(self.apm_config)

        # Configurar APM manager
        apm_manager = configure_apm(apm_config)

        # Registrar en el contenedor DI
        self.application.container.register(
            "apm_manager", ComponentProvider(lambda: apm_manager, singleton=True)
        )

        # Cargar addons APM si están configurados
        self._load_apm_addons(apm_config)

    def _load_apm_addons(self, apm_config: APMConfig) -> None:
        """Carga addons APM configurados."""
        try:
            # Importar addons dinámicamente
            if self.apm_config.get("newrelic", {}).get("enabled", False):
                self._load_apm_addon(
                    "addons.apm.newrelic", "NewRelicAPMAddon", self.apm_config.get("newrelic", {})
                )

            if self.apm_config.get("datadog", {}).get("enabled", False):
                self._load_apm_addon(
                    "addons.apm.datadog", "DataDogAPMAddon", self.apm_config.get("datadog", {})
                )

        except ImportError as e:
            # Log warning but continue
            print(f"Warning: Could not load APM addon: {e}")

    def _load_apm_addon(self, module_name: str, class_name: str, config: dict[str, Any]) -> None:
        """Carga un addon APM específico."""
        try:
            import importlib

            module = importlib.import_module(module_name)
            addon_class = getattr(module, class_name)

            # Crear instancia del addon
            addon = addon_class(self.application, config)
            addon.configure()

        except (ImportError, AttributeError) as e:
            print(f"Warning: Could not load APM addon {module_name}.{class_name}: {e}")

    def _configure_health(self) -> None:
        """Configura el sistema de health checks."""
        if not self.health_config.get("enabled", True):
            return

        # Obtener versión de la configuración o usar la del proyecto
        version = self.health_config.get("version", self.application.config.project_version)

        health_checker = HealthChecker(version)

        # Registrar en el contenedor DI
        self.application.container.register(
            "health_checker", ComponentProvider(lambda: health_checker, singleton=True)
        )

    def is_configured(self) -> bool:
        """
        Verifica si el starter ha sido configurado.

        Returns:
            True si está configurado, False en caso contrario.
        """
        return self._configured
