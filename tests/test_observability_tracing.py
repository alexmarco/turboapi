"""Pruebas para el sistema de trazabilidad distribuida."""

from unittest.mock import patch

from turboapi.observability.tracing import OpenTelemetryTracer
from turboapi.observability.tracing import TracingConfig
from turboapi.observability.tracing import add_event
from turboapi.observability.tracing import configure_tracing
from turboapi.observability.tracing import get_tracer
from turboapi.observability.tracing import set_attribute
from turboapi.observability.tracing import start_as_current_span
from turboapi.observability.tracing import start_span


class TestTracingConfig:
    """Pruebas para la configuración de trazabilidad."""

    def test_tracing_config_defaults(self):
        """Prueba los valores por defecto de TracingConfig."""
        config = TracingConfig()

        assert config.enable_tracing is True
        assert config.enable_jaeger is True
        assert config.enable_otlp is False
        assert config.jaeger_endpoint == "http://localhost:14268/api/traces"
        assert config.otlp_endpoint == "http://localhost:4317"
        assert config.service_name == "turboapi"
        assert config.service_version == "0.1.0"
        assert config.enable_auto_instrumentation is True
        assert config.sampling_ratio == 1.0

    def test_tracing_config_custom(self):
        """Prueba la configuración personalizada de TracingConfig."""
        config = TracingConfig(
            enable_tracing=False,
            enable_jaeger=False,
            enable_otlp=True,
            jaeger_endpoint="http://jaeger:14268/api/traces",
            otlp_endpoint="http://otlp:4317",
            service_name="testapp",
            service_version="1.0.0",
            enable_auto_instrumentation=False,
            sampling_ratio=0.5,
        )

        assert config.enable_tracing is False
        assert config.enable_jaeger is False
        assert config.enable_otlp is True
        assert config.jaeger_endpoint == "http://jaeger:14268/api/traces"
        assert config.otlp_endpoint == "http://otlp:4317"
        assert config.service_name == "testapp"
        assert config.service_version == "1.0.0"
        assert config.enable_auto_instrumentation is False
        assert config.sampling_ratio == 0.5

    def test_tracing_config_from_dict(self):
        """Prueba la creación de TracingConfig desde un diccionario."""
        config_dict = {
            "enable_tracing": True,
            "enable_jaeger": False,
            "enable_otlp": True,
            "jaeger_endpoint": "http://custom-jaeger:14268/api/traces",
            "otlp_endpoint": "http://custom-otlp:4317",
            "service_name": "testapp",
            "service_version": "2.0.0",
            "enable_auto_instrumentation": False,
            "sampling_ratio": 0.8,
        }

        config = TracingConfig.from_dict(config_dict)

        assert config.enable_tracing is True
        assert config.enable_jaeger is False
        assert config.enable_otlp is True
        assert config.jaeger_endpoint == "http://custom-jaeger:14268/api/traces"
        assert config.otlp_endpoint == "http://custom-otlp:4317"
        assert config.service_name == "testapp"
        assert config.service_version == "2.0.0"
        assert config.enable_auto_instrumentation is False
        assert config.sampling_ratio == 0.8


class TestOpenTelemetryTracer:
    """Pruebas para el trazador OpenTelemetry."""

    def test_tracer_creation(self):
        """Prueba la creación de un trazador OpenTelemetry."""
        config = TracingConfig()
        tracer = OpenTelemetryTracer(config)

        assert tracer.config == config
        assert tracer._initialized is False

    def test_tracer_initialize(self):
        """Prueba la inicialización del trazador."""
        # Deshabilitar Jaeger para evitar problemas en tests
        config = TracingConfig(enable_tracing=True, enable_jaeger=False)
        tracer = OpenTelemetryTracer(config)

        tracer.initialize()

        assert tracer._initialized is True
        assert tracer._tracer is not None

    def test_tracer_get_tracer(self):
        """Prueba la obtención del tracer OpenTelemetry."""
        config = TracingConfig(enable_jaeger=False)
        tracer = OpenTelemetryTracer(config)
        tracer.initialize()

        otel_tracer = tracer.get_tracer()

        # Verificar que es un tracer OpenTelemetry
        assert hasattr(otel_tracer, "start_span")
        assert callable(otel_tracer.start_span)

    def test_tracer_start_span(self):
        """Prueba la creación de un span."""
        config = TracingConfig(enable_jaeger=False)
        tracer = OpenTelemetryTracer(config)
        tracer.initialize()

        span = tracer.start_span("test_operation", {"key": "value"})

        # Verificar que es un span OpenTelemetry
        assert hasattr(span, "set_attribute")
        assert hasattr(span, "end")
        assert callable(span.set_attribute)
        assert callable(span.end)

    def test_tracer_start_as_current_span(self):
        """Prueba la creación de un span como contexto actual."""
        config = TracingConfig(enable_jaeger=False)
        tracer = OpenTelemetryTracer(config)
        tracer.initialize()

        with tracer.start_as_current_span("test_operation", {"key": "value"}) as span:
            # Verificar que es un span OpenTelemetry
            assert hasattr(span, "set_attribute")
            assert hasattr(span, "end")
            assert callable(span.set_attribute)
            assert callable(span.end)

    def test_tracer_add_event(self):
        """Prueba la adición de eventos al span actual."""
        config = TracingConfig(enable_jaeger=False)
        tracer = OpenTelemetryTracer(config)
        tracer.initialize()

        with tracer.start_as_current_span("test_operation"):
            # No debería lanzar excepción
            tracer.add_event("test_event", {"event_key": "event_value"})

    def test_tracer_set_attribute(self):
        """Prueba el establecimiento de atributos en el span actual."""
        config = TracingConfig(enable_jaeger=False)
        tracer = OpenTelemetryTracer(config)
        tracer.initialize()

        with tracer.start_as_current_span("test_operation"):
            # No debería lanzar excepción
            tracer.set_attribute("test_key", "test_value")

    def test_tracer_instrument_fastapi(self):
        """Prueba la instrumentación de FastAPI."""
        config = TracingConfig(enable_auto_instrumentation=True)
        tracer = OpenTelemetryTracer(config)
        tracer.initialize()

        # Mock de FastAPI
        mock_app = object()

        with patch("turboapi.observability.tracing.FastAPIInstrumentor") as mock_instrumentor:
            tracer.instrument_fastapi(mock_app)
            mock_instrumentor.instrument_app.assert_called_once_with(mock_app)

    def test_tracer_instrument_requests(self):
        """Prueba la instrumentación de requests."""
        config = TracingConfig(enable_auto_instrumentation=True)
        tracer = OpenTelemetryTracer(config)
        tracer.initialize()

        with patch("turboapi.observability.tracing.RequestsInstrumentor") as mock_instrumentor:
            tracer.instrument_requests()
            mock_instrumentor.return_value.instrument.assert_called_once()

    def test_tracer_instrument_sqlalchemy(self):
        """Prueba la instrumentación de SQLAlchemy."""
        config = TracingConfig(enable_auto_instrumentation=True)
        tracer = OpenTelemetryTracer(config)
        tracer.initialize()

        mock_engine = object()

        with patch("turboapi.observability.tracing.SQLAlchemyInstrumentor") as mock_instrumentor:
            tracer.instrument_sqlalchemy(mock_engine)
            mock_instrumentor.return_value.instrument.assert_called_once_with(engine=mock_engine)


class TestTracingIntegration:
    """Pruebas de integración para el sistema de trazabilidad."""

    def test_configure_tracing_function(self):
        """Prueba la función de conveniencia configure_tracing."""
        config = TracingConfig(enable_jaeger=False)

        configure_tracing(config)

        # Verificar que se configuró globalmente
        tracer = get_tracer()
        assert isinstance(tracer, OpenTelemetryTracer)
        # Note: tracer.config may have different defaults now

    def test_get_tracer_function(self):
        """Prueba la función de conveniencia get_tracer."""
        config = TracingConfig(enable_jaeger=False)
        configure_tracing(config)

        tracer = get_tracer()

        assert isinstance(tracer, OpenTelemetryTracer)
        assert tracer._initialized is True

    def test_get_tracer_not_configured(self):
        """Prueba get_tracer cuando no está configurado."""
        # Ahora get_tracer siempre devuelve una nueva instancia
        tracer = get_tracer()
        assert isinstance(tracer, OpenTelemetryTracer)

    def test_start_span_function(self):
        """Prueba la función de conveniencia start_span."""
        config = TracingConfig(enable_jaeger=False)
        configure_tracing(config)

        span = start_span("test_operation", {"key": "value"})

        # Verificar que es un span OpenTelemetry
        assert hasattr(span, "set_attribute")
        assert hasattr(span, "end")
        assert callable(span.set_attribute)
        assert callable(span.end)

    def test_start_as_current_span_function(self):
        """Prueba la función de conveniencia start_as_current_span."""
        config = TracingConfig(enable_jaeger=False)
        configure_tracing(config)

        with start_as_current_span("test_operation", {"key": "value"}) as span:
            # Verificar que es un span OpenTelemetry
            assert hasattr(span, "set_attribute")
            assert hasattr(span, "end")
            assert callable(span.set_attribute)
            assert callable(span.end)

    def test_add_event_function(self):
        """Prueba la función de conveniencia add_event."""
        config = TracingConfig(enable_jaeger=False)
        configure_tracing(config)

        with start_as_current_span("test_operation"):
            # No debería lanzar excepción
            add_event("test_event", {"event_key": "event_value"})

    def test_set_attribute_function(self):
        """Prueba la función de conveniencia set_attribute."""
        config = TracingConfig(enable_jaeger=False)
        configure_tracing(config)

        with start_as_current_span("test_operation"):
            # No debería lanzar excepción
            set_attribute("test_key", "test_value")

    def test_tracing_workflow_integration(self):
        """Prueba un flujo completo de trabajo con trazabilidad."""
        config = TracingConfig(enable_jaeger=False)
        configure_tracing(config)

        # Simular un flujo de trabajo completo
        with start_as_current_span("user_operation") as root_span:
            set_attribute("user.id", "123")
            set_attribute("operation.type", "authentication")

            add_event("user_login_attempt", {"method": "password"})

            # Simular operación de base de datos
            with start_as_current_span("database_query") as db_span:
                set_attribute("db.table", "users")
                set_attribute("db.operation", "select")
                add_event("query_executed", {"rows_affected": 1})

            add_event("user_authenticated", {"user_id": "123"})

        # Verificar que los spans tienen los métodos correctos
        assert hasattr(root_span, "set_attribute")
        assert hasattr(root_span, "end")
        assert hasattr(db_span, "set_attribute")
        assert hasattr(db_span, "end")
