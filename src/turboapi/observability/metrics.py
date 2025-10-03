"""Sistema de métricas basado en OpenTelemetry para TurboAPI."""

from dataclasses import dataclass
from typing import Any

from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.system_metrics import SystemMetricsInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource


@dataclass
class MetricConfig:
    """Configuración para el sistema de métricas."""

    enable_otel: bool = True
    enable_prometheus_export: bool = True
    prometheus_port: int = 8000
    prometheus_path: str = "/metrics"
    otel_service_name: str = "turboapi"
    enable_default_metrics: bool = True
    enable_system_metrics: bool = True

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "MetricConfig":
        """
        Crea MetricConfig desde un diccionario.

        Parameters
        ----------
        config_dict : dict[str, Any]
            Diccionario de configuración.

        Returns
        -------
        MetricConfig
            Configuración de métricas.

        Examples
        --------
        >>> config = MetricConfig.from_dict({
        ...     "enable_otel": True,
        ...     "prometheus_port": 8080
        ... })
        """
        return cls(
            enable_otel=config_dict.get("enable_otel", True),
            enable_prometheus_export=config_dict.get("enable_prometheus_export", True),
            prometheus_port=config_dict.get("prometheus_port", 8000),
            prometheus_path=config_dict.get("prometheus_path", "/metrics"),
            otel_service_name=config_dict.get("otel_service_name", "turboapi"),
            enable_default_metrics=config_dict.get("enable_default_metrics", True),
            enable_system_metrics=config_dict.get("enable_system_metrics", True),
        )


class OpenTelemetryCollector:
    """Recolector de métricas basado en OpenTelemetry."""

    def __init__(self, config: MetricConfig):
        """
        Inicializa el recolector de métricas.

        Parameters
        ----------
        config : MetricConfig
            Configuración del sistema de métricas.

        Examples
        --------
        >>> config = MetricConfig(enable_otel=True)
        >>> collector = OpenTelemetryCollector(config)
        """
        self.config = config
        self._initialized = False
        self._meter: Any = None
        self._system_instrumentor: SystemMetricsInstrumentor | None = None

    def initialize(self) -> None:
        """
        Inicializa el sistema de métricas OpenTelemetry.

        Examples
        --------
        >>> collector = OpenTelemetryCollector(MetricConfig())
        >>> collector.initialize()
        """
        if self._initialized:
            return

        if not self.config.enable_otel:
            return

        # Crear resource con información del servicio
        resource = Resource.create(
            {
                "service.name": self.config.otel_service_name,
                "service.version": "0.1.0",
            }
        )

        # Configurar exportadores
        readers = []
        if self.config.enable_prometheus_export:
            prometheus_reader = PrometheusMetricReader()
            readers.append(prometheus_reader)

        # Crear MeterProvider
        meter_provider = MeterProvider(
            resource=resource,
            metric_readers=readers,
        )

        # Configurar el provider global
        metrics.set_meter_provider(meter_provider)

        # Obtener el meter
        self._meter = metrics.get_meter("turboapi")

        # Instrumentar métricas del sistema si está habilitado
        if self.config.enable_system_metrics:
            self._system_instrumentor = SystemMetricsInstrumentor()
            self._system_instrumentor.instrument()

        self._initialized = True

    def _ensure_initialized(self) -> None:
        """Asegura que el recolector esté inicializado."""
        if not self._initialized:
            self.initialize()

    def counter(self, name: str, description: str) -> Any:
        """
        Crea un contador OpenTelemetry nativo.

        Parameters
        ----------
        name : str
            Nombre de la métrica.
        description : str
            Descripción de la métrica.

        Returns
        -------
        Counter
            Contador OpenTelemetry nativo.

        Examples
        --------
        >>> collector = OpenTelemetryCollector(MetricConfig())
        >>> collector.initialize()
        >>> counter = collector.counter("requests_total", "Total requests")
        >>> counter.add(1, {"method": "GET"})
        """
        self._ensure_initialized()
        if self._meter is None:
            raise RuntimeError("Meter not initialized")
        return self._meter.create_counter(name=name, description=description)

    def gauge(self, name: str, description: str) -> Any:
        """
        Crea un gauge OpenTelemetry nativo (up_down_counter).

        Parameters
        ----------
        name : str
            Nombre de la métrica.
        description : str
            Descripción de la métrica.

        Returns
        -------
        UpDownCounter
            Gauge OpenTelemetry nativo.

        Examples
        --------
        >>> collector = OpenTelemetryCollector(MetricConfig())
        >>> collector.initialize()
        >>> gauge = collector.gauge("active_connections", "Active connections")
        >>> gauge.add(1, {"instance": "server1"})
        """
        self._ensure_initialized()
        if self._meter is None:
            raise RuntimeError("Meter not initialized")
        return self._meter.create_up_down_counter(name=name, description=description)

    def histogram(self, name: str, description: str) -> Any:
        """
        Crea un histograma OpenTelemetry nativo.

        Parameters
        ----------
        name : str
            Nombre de la métrica.
        description : str
            Descripción de la métrica.

        Returns
        -------
        Histogram
            Histograma OpenTelemetry nativo.

        Examples
        --------
        >>> collector = OpenTelemetryCollector(MetricConfig())
        >>> collector.initialize()
        >>> histogram = collector.histogram("request_duration", "Request duration")
        >>> histogram.record(0.1, {"method": "GET"})
        """
        self._ensure_initialized()
        if self._meter is None:
            raise RuntimeError("Meter not initialized")
        return self._meter.create_histogram(name=name, description=description)

    def summary(self, name: str, description: str) -> Any:
        """
        Crea un resumen OpenTelemetry nativo (implementado como histogram).

        Parameters
        ----------
        name : str
            Nombre de la métrica.
        description : str
            Descripción de la métrica.

        Returns
        -------
        Histogram
            Resumen OpenTelemetry nativo (como histogram).

        Examples
        --------
        >>> collector = OpenTelemetryCollector(MetricConfig())
        >>> collector.initialize()
        >>> summary = collector.summary("response_size", "Response size")
        >>> summary.record(1024, {"endpoint": "/api/users"})
        """
        self._ensure_initialized()
        if self._meter is None:
            raise RuntimeError("Meter not initialized")
        # OpenTelemetry no tiene summary nativo, usamos histogram
        return self._meter.create_histogram(name=name, description=description)

    def get_system_metrics(self) -> dict[str, Any]:
        """
        Obtiene métricas del sistema desde OpenTelemetry.

        Returns
        -------
        dict[str, Any]
            Métricas del sistema obtenidas desde OpenTelemetry.

        Examples
        --------
        >>> collector = OpenTelemetryCollector(MetricConfig())
        >>> collector.initialize()
        >>> metrics = collector.get_system_metrics()
        >>> print(metrics['cpu_percent'])
        """
        self._ensure_initialized()

        # Intentar importar psutil para obtener métricas del sistema
        try:
            import psutil
        except ImportError:
            return {
                "cpu_percent": 0.0,
                "memory_total": 0,
                "memory_available": 0,
                "memory_percent": 0.0,
                "disk_total": 0,
                "disk_used": 0,
                "disk_free": 0,
                "disk_percent": 0.0,
            }

        try:
            # Obtener métricas del sistema
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "cpu_percent": cpu_percent,
                "memory_total": memory.total,
                "memory_available": memory.available,
                "memory_percent": memory.percent,
                "disk_total": disk.total,
                "disk_used": disk.used,
                "disk_free": disk.free,
                "disk_percent": disk.percent,
            }
        except Exception:
            return {
                "cpu_percent": 0.0,
                "memory_total": 0,
                "memory_available": 0,
                "memory_percent": 0.0,
                "disk_total": 0,
                "disk_used": 0,
                "disk_free": 0,
                "disk_percent": 0.0,
            }

    def get_process_metrics(self) -> dict[str, Any]:
        """
        Obtiene métricas del proceso desde OpenTelemetry.

        Returns
        -------
        dict[str, Any]
            Métricas del proceso obtenidas desde OpenTelemetry.

        Examples
        --------
        >>> collector = OpenTelemetryCollector(MetricConfig())
        >>> collector.initialize()
        >>> metrics = collector.get_process_metrics()
        >>> print(metrics['memory_usage'])
        """
        self._ensure_initialized()

        # Intentar importar psutil para obtener métricas del proceso
        try:
            import psutil
        except ImportError:
            return {
                "pid": 0,
                "memory_rss": 0,
                "memory_vms": 0,
                "memory_percent": 0.0,
                "cpu_percent": 0.0,
                "num_threads": 1,
                "num_fds": None,
            }

        try:
            # Obtener métricas del proceso
            process = psutil.Process()
            memory_info = process.memory_info()

            return {
                "pid": process.pid,
                "memory_rss": memory_info.rss,
                "memory_vms": memory_info.vms,
                "memory_percent": process.memory_percent(),
                "cpu_percent": process.cpu_percent(),
                "num_threads": process.num_threads(),
                "num_fds": process.num_fds() if hasattr(process, "num_fds") else None,
            }
        except Exception:
            return {
                "pid": 0,
                "memory_rss": 0,
                "memory_vms": 0,
                "memory_percent": 0.0,
                "cpu_percent": 0.0,
                "num_threads": 1,
                "num_fds": None,
            }


# Funciones de conveniencia para compatibilidad con código existente
# Estas funciones están deprecadas y se recomienda usar inyección de dependencias


def configure_metrics(config: MetricConfig) -> OpenTelemetryCollector:
    """
    Configura el sistema de métricas.

    Parameters
    ----------
    config : MetricConfig
        Configuración del sistema de métricas.

    Returns
    -------
    OpenTelemetryCollector
        Instancia del recolector de métricas configurado.

    Examples
    --------
    >>> config = MetricConfig(enable_otel=True, enable_prometheus_export=True)
    >>> collector = configure_metrics(config)

    Note
    ----
    Esta función está deprecada. Se recomienda usar inyección de dependencias
    a través del contenedor DI del framework.
    """
    collector = OpenTelemetryCollector(config)
    collector.initialize()
    return collector


def get_metrics_collector() -> OpenTelemetryCollector:
    """
    Obtiene una nueva instancia del recolector de métricas.

    Returns
    -------
    OpenTelemetryCollector
        Nueva instancia del recolector de métricas.

    Examples
    --------
    >>> collector = get_metrics_collector()
    >>> counter = collector.counter("requests", "Total requests")

    Note
    ----
    Esta función está deprecada. Se recomienda usar inyección de dependencias
    a través del contenedor DI del framework.
    """
    # Crear una instancia temporal para compatibilidad
    config = MetricConfig()
    collector = OpenTelemetryCollector(config)
    collector.initialize()
    return collector


# Funciones de conveniencia que retornan métricas OpenTelemetry nativas
def create_counter(name: str, description: str) -> Any:
    """
    Crea un contador usando el recolector global.

    Parameters
    ----------
    name : str
        Nombre de la métrica.
    description : str
        Descripción de la métrica.

    Returns
    -------
    Counter
        Contador OpenTelemetry nativo.

    Examples
    --------
    >>> counter = create_counter("requests_total", "Total requests")
    >>> counter.add(1, {"method": "GET"})
    """
    collector = get_metrics_collector()
    return collector.counter(name, description)


def create_gauge(name: str, description: str) -> Any:
    """
    Crea un gauge usando el recolector global.

    Parameters
    ----------
    name : str
        Nombre de la métrica.
    description : str
        Descripción de la métrica.

    Returns
    -------
    UpDownCounter
        Gauge OpenTelemetry nativo.

    Examples
    --------
    >>> gauge = create_gauge("active_connections", "Active connections")
    >>> gauge.add(1, {"instance": "server1"})
    """
    collector = get_metrics_collector()
    return collector.gauge(name, description)


def create_histogram(name: str, description: str) -> Any:
    """
    Crea un histograma usando el recolector global.

    Parameters
    ----------
    name : str
        Nombre de la métrica.
    description : str
        Descripción de la métrica.

    Returns
    -------
    Histogram
        Histograma OpenTelemetry nativo.

    Examples
    --------
    >>> histogram = create_histogram("request_duration", "Request duration")
    >>> histogram.record(0.1, {"method": "GET"})
    """
    collector = get_metrics_collector()
    return collector.histogram(name, description)


def get_system_metrics() -> dict[str, Any]:
    """
    Obtiene métricas del sistema desde OpenTelemetry.

    Returns
    -------
    dict[str, Any]
        Métricas del sistema obtenidas desde OpenTelemetry.

    Examples
    --------
    >>> metrics = get_system_metrics()
    >>> print(metrics['cpu_percent'])
    """
    collector = get_metrics_collector()
    return collector.get_system_metrics()


def get_process_metrics() -> dict[str, Any]:
    """
    Obtiene métricas del proceso desde OpenTelemetry.

    Returns
    -------
    dict[str, Any]
        Métricas del proceso obtenidas desde OpenTelemetry.

    Examples
    --------
    >>> metrics = get_process_metrics()
    >>> print(metrics['memory_usage'])
    """
    collector = get_metrics_collector()
    return collector.get_process_metrics()


def create_summary(name: str, description: str) -> Any:
    """
    Crea un resumen usando el recolector global.

    Parameters
    ----------
    name : str
        Nombre de la métrica.
    description : str
        Descripción de la métrica.

    Returns
    -------
    Histogram
        Resumen OpenTelemetry nativo (como histogram).

    Examples
    --------
    >>> summary = create_summary("response_size", "Response size")
    >>> summary.record(1024, {"endpoint": "/api/users"})
    """
    collector = get_metrics_collector()
    return collector.summary(name, description)
