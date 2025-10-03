"""Sistema de trazabilidad distribuida basado en OpenTelemetry para TurboAPI."""

from dataclasses import dataclass
from typing import Any

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


@dataclass
class TracingConfig:
    """Configuración para el sistema de trazabilidad distribuida."""

    enable_tracing: bool = True
    enable_jaeger: bool = True
    enable_otlp: bool = False
    jaeger_endpoint: str = "http://localhost:14268/api/traces"
    otlp_endpoint: str = "http://localhost:4317"
    service_name: str = "turboapi"
    service_version: str = "0.1.0"
    enable_auto_instrumentation: bool = True
    sampling_ratio: float = 1.0

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "TracingConfig":
        """
        Crea TracingConfig desde un diccionario.

        Parameters
        ----------
        config_dict : dict[str, Any]
            Diccionario de configuración.

        Returns
        -------
        TracingConfig
            Configuración de trazabilidad.

        Examples
        --------
        >>> config = TracingConfig.from_dict({
        ...     "enable_tracing": True,
        ...     "jaeger_endpoint": "http://jaeger:14268/api/traces"
        ... })
        """
        return cls(
            enable_tracing=config_dict.get("enable_tracing", True),
            enable_jaeger=config_dict.get("enable_jaeger", True),
            enable_otlp=config_dict.get("enable_otlp", False),
            jaeger_endpoint=config_dict.get("jaeger_endpoint", "http://localhost:14268/api/traces"),
            otlp_endpoint=config_dict.get("otlp_endpoint", "http://localhost:4317"),
            service_name=config_dict.get("service_name", "turboapi"),
            service_version=config_dict.get("service_version", "0.1.0"),
            enable_auto_instrumentation=config_dict.get("enable_auto_instrumentation", True),
            sampling_ratio=config_dict.get("sampling_ratio", 1.0),
        )


class OpenTelemetryTracer:
    """Trazador OpenTelemetry para TurboAPI."""

    def __init__(self, config: TracingConfig):
        """
        Inicializa el trazador OpenTelemetry.

        Parameters
        ----------
        config : TracingConfig
            Configuración del sistema de trazabilidad.

        Examples
        --------
        >>> config = TracingConfig(enable_tracing=True)
        >>> tracer = OpenTelemetryTracer(config)
        """
        self.config = config
        self._initialized = False
        self._tracer: Any = None

    def initialize(self) -> None:
        """
        Inicializa el sistema de trazabilidad OpenTelemetry.

        Examples
        --------
        >>> tracer = OpenTelemetryTracer(TracingConfig())
        >>> tracer.initialize()
        """
        if self._initialized:
            return

        if not self.config.enable_tracing:
            return

        # Crear resource con información del servicio
        resource = Resource.create(
            {
                "service.name": self.config.service_name,
                "service.version": self.config.service_version,
            }
        )

        # Crear TracerProvider
        tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(tracer_provider)

        # Configurar exportadores
        if self.config.enable_jaeger:
            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=6831,
                collector_endpoint=self.config.jaeger_endpoint,
            )
            span_processor = BatchSpanProcessor(jaeger_exporter)
            tracer_provider.add_span_processor(span_processor)

        if self.config.enable_otlp:
            otlp_exporter = OTLPSpanExporter(endpoint=self.config.otlp_endpoint)
            span_processor = BatchSpanProcessor(otlp_exporter)
            tracer_provider.add_span_processor(span_processor)

        # Obtener el tracer
        self._tracer = trace.get_tracer(__name__)

        self._initialized = True

    def _ensure_initialized(self) -> None:
        """Asegura que el trazador esté inicializado."""
        if not self._initialized:
            self.initialize()

    def get_tracer(self) -> Any:
        """
        Obtiene el tracer OpenTelemetry.

        Returns
        -------
        Tracer
            Tracer OpenTelemetry.

        Examples
        --------
        >>> tracer = OpenTelemetryTracer(TracingConfig())
        >>> tracer.initialize()
        >>> otel_tracer = tracer.get_tracer()
        >>> with otel_tracer.start_as_current_span("operation"):
        ...     pass
        """
        self._ensure_initialized()
        if self._tracer is None:
            raise RuntimeError("Tracer not initialized")
        return self._tracer

    def start_span(self, name: str, attributes: dict[str, Any] | None = None) -> Any:
        """
        Inicia un nuevo span.

        Parameters
        ----------
        name : str
            Nombre del span.
        attributes : dict[str, Any], optional
            Atributos del span.

        Returns
        -------
        Span
            Span OpenTelemetry.

        Examples
        --------
        >>> tracer = OpenTelemetryTracer(TracingConfig())
        >>> tracer.initialize()
        >>> span = tracer.start_span("database_query", {"table": "users"})
        >>> # ... hacer operación ...
        >>> span.end()
        """
        self._ensure_initialized()
        if self._tracer is None:
            raise RuntimeError("Tracer not initialized")

        span = self._tracer.start_span(name)
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        return span

    def start_as_current_span(self, name: str, attributes: dict[str, Any] | None = None) -> Any:
        """
        Inicia un nuevo span como span actual.

        Parameters
        ----------
        name : str
            Nombre del span.
        attributes : dict[str, Any], optional
            Atributos del span.

        Returns
        -------
        Span
            Span OpenTelemetry como contexto actual.

        Examples
        --------
        >>> tracer = OpenTelemetryTracer(TracingConfig())
        >>> tracer.initialize()
        >>> with tracer.start_as_current_span("operation") as span:
        ...     span.set_attribute("key", "value")
        ...     # operación dentro del span
        """
        self._ensure_initialized()
        if self._tracer is None:
            raise RuntimeError("Tracer not initialized")

        span_context = self._tracer.start_as_current_span(name)

        # Crear un wrapper que permita establecer atributos
        class SpanWrapper:
            def __init__(self, context_manager: Any, attrs: dict[str, Any] | None = None) -> None:
                self._context_manager = context_manager
                self._attrs = attrs or {}

            def __enter__(self) -> Any:
                self._span = self._context_manager.__enter__()
                # Establecer atributos después de entrar al contexto
                for key, value in self._attrs.items():
                    self._span.set_attribute(key, value)
                return self._span

            def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> Any:
                return self._context_manager.__exit__(exc_type, exc_val, exc_tb)

        return SpanWrapper(span_context, attributes)

    def add_event(self, name: str, attributes: dict[str, Any] | None = None) -> None:
        """
        Añade un evento al span actual.

        Parameters
        ----------
        name : str
            Nombre del evento.
        attributes : dict[str, Any], optional
            Atributos del evento.

        Examples
        --------
        >>> tracer = OpenTelemetryTracer(TracingConfig())
        >>> tracer.initialize()
        >>> with tracer.start_as_current_span("operation"):
        ...     tracer.add_event("user_authenticated", {"user_id": "123"})
        """
        current_span = trace.get_current_span()
        if current_span and current_span.is_recording():
            current_span.add_event(name, attributes or {})

    def set_attribute(self, key: str, value: Any) -> None:
        """
        Establece un atributo en el span actual.

        Parameters
        ----------
        key : str
            Clave del atributo.
        value : Any
            Valor del atributo.

        Examples
        --------
        >>> tracer = OpenTelemetryTracer(TracingConfig())
        >>> tracer.initialize()
        >>> with tracer.start_as_current_span("operation"):
        ...     tracer.set_attribute("user.id", "123")
        """
        current_span = trace.get_current_span()
        if current_span and current_span.is_recording():
            current_span.set_attribute(key, value)

    def instrument_fastapi(self, app: Any) -> None:
        """
        Instrumenta una aplicación FastAPI.

        Parameters
        ----------
        app : FastAPI
            Aplicación FastAPI a instrumentar.

        Examples
        --------
        >>> from fastapi import FastAPI
        >>> app = FastAPI()
        >>> tracer = OpenTelemetryTracer(TracingConfig())
        >>> tracer.initialize()
        >>> tracer.instrument_fastapi(app)
        """
        if not self.config.enable_auto_instrumentation:
            return

        self._ensure_initialized()
        FastAPIInstrumentor.instrument_app(app)

    def instrument_requests(self) -> None:
        """
        Instrumenta la librería requests.

        Examples
        --------
        >>> tracer = OpenTelemetryTracer(TracingConfig())
        >>> tracer.initialize()
        >>> tracer.instrument_requests()
        """
        if not self.config.enable_auto_instrumentation:
            return

        self._ensure_initialized()
        RequestsInstrumentor().instrument()

    def instrument_sqlalchemy(self, engine: Any) -> None:
        """
        Instrumenta SQLAlchemy.

        Parameters
        ----------
        engine : Engine
            Motor de SQLAlchemy a instrumentar.

        Examples
        --------
        >>> from sqlalchemy import create_engine
        >>> engine = create_engine("sqlite:///test.db")
        >>> tracer = OpenTelemetryTracer(TracingConfig())
        >>> tracer.initialize()
        >>> tracer.instrument_sqlalchemy(engine)
        """
        if not self.config.enable_auto_instrumentation:
            return

        self._ensure_initialized()
        SQLAlchemyInstrumentor().instrument(engine=engine)


# Funciones de conveniencia para compatibilidad con código existente
# Estas funciones están deprecadas y se recomienda usar inyección de dependencias


def configure_tracing(config: TracingConfig) -> OpenTelemetryTracer:
    """
    Configura el sistema de trazabilidad.

    Parameters
    ----------
    config : TracingConfig
        Configuración del sistema de trazabilidad.

    Returns
    -------
    OpenTelemetryTracer
        Instancia del trazador configurado.

    Examples
    --------
    >>> config = TracingConfig(enable_tracing=True, enable_jaeger=True)
    >>> tracer = configure_tracing(config)

    Note
    ----
    Esta función está deprecada. Se recomienda usar inyección de dependencias
    a través del contenedor DI del framework.
    """
    tracer = OpenTelemetryTracer(config)
    tracer.initialize()
    return tracer


def get_tracer() -> OpenTelemetryTracer:
    """
    Obtiene una nueva instancia del trazador.

    Returns
    -------
    OpenTelemetryTracer
        Nueva instancia del trazador.

    Examples
    --------
    >>> tracer = get_tracer()
    >>> with tracer.start_as_current_span("operation"):
    ...     pass

    Note
    ----
    Esta función está deprecada. Se recomienda usar inyección de dependencias
    a través del contenedor DI del framework.
    """
    # Crear una instancia temporal para compatibilidad
    config = TracingConfig()
    tracer = OpenTelemetryTracer(config)
    tracer.initialize()
    return tracer


# Funciones de conveniencia
def start_span(name: str, attributes: dict[str, Any] | None = None) -> Any:
    """
    Inicia un nuevo span usando el trazador global.

    Parameters
    ----------
    name : str
        Nombre del span.
    attributes : dict[str, Any], optional
        Atributos del span.

    Returns
    -------
    Span
        Span OpenTelemetry.

    Examples
    --------
    >>> span = start_span("database_query", {"table": "users"})
    >>> # ... hacer operación ...
    >>> span.end()
    """
    tracer = get_tracer()
    return tracer.start_span(name, attributes)


def start_as_current_span(name: str, attributes: dict[str, Any] | None = None) -> Any:
    """
    Inicia un nuevo span como span actual usando el trazador global.

    Parameters
    ----------
    name : str
        Nombre del span.
    attributes : dict[str, Any], optional
        Atributos del span.

    Returns
    -------
    Span
        Span OpenTelemetry como contexto actual.

    Examples
    --------
    >>> with start_as_current_span("operation") as span:
    ...     span.set_attribute("key", "value")
    ...     # operación dentro del span
    """
    tracer = get_tracer()
    return tracer.start_as_current_span(name, attributes)


def add_event(name: str, attributes: dict[str, Any] | None = None) -> None:
    """
    Añade un evento al span actual usando el trazador global.

    Parameters
    ----------
    name : str
        Nombre del evento.
    attributes : dict[str, Any], optional
        Atributos del evento.

    Examples
    --------
    >>> with start_as_current_span("operation"):
    ...     add_event("user_authenticated", {"user_id": "123"})
    """
    tracer = get_tracer()
    tracer.add_event(name, attributes)


def set_attribute(key: str, value: Any) -> None:
    """
    Establece un atributo en el span actual usando el trazador global.

    Parameters
    ----------
    key : str
        Clave del atributo.
    value : Any
        Valor del atributo.

    Examples
    --------
    >>> with start_as_current_span("operation"):
    ...     set_attribute("user.id", "123")
    """
    tracer = get_tracer()
    tracer.set_attribute(key, value)
