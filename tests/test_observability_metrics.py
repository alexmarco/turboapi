"""Pruebas para el sistema de métricas de TurboAPI."""

from unittest.mock import patch

from turboapi.observability.metrics import MetricConfig
from turboapi.observability.metrics import OpenTelemetryCollector
from turboapi.observability.metrics import create_counter
from turboapi.observability.metrics import create_gauge
from turboapi.observability.metrics import create_histogram
from turboapi.observability.metrics import create_summary
from turboapi.observability.metrics import get_metrics_collector


class TestMetricConfig:
    """Pruebas para la configuración de métricas."""

    def test_metric_config_defaults(self):
        """Prueba los valores por defecto de MetricConfig."""
        config = MetricConfig()

        assert config.enable_otel is True
        assert config.enable_prometheus_export is True
        assert config.prometheus_port == 8000
        assert config.prometheus_path == "/metrics"
        assert config.otel_service_name == "turboapi"
        assert config.enable_default_metrics is True

    def test_metric_config_custom(self):
        """Prueba MetricConfig con valores personalizados."""
        config = MetricConfig(
            enable_otel=True,
            enable_prometheus_export=False,
            prometheus_port=9000,
            prometheus_path="/custom-metrics",
            otel_service_name="myapp",
            enable_default_metrics=False,
        )

        assert config.enable_otel is True
        assert config.enable_prometheus_export is False
        assert config.prometheus_port == 9000
        assert config.prometheus_path == "/custom-metrics"
        assert config.otel_service_name == "myapp"
        assert config.enable_default_metrics is False

    def test_metric_config_from_dict(self):
        """Prueba la creación de MetricConfig desde un diccionario."""
        config_dict = {
            "enable_otel": True,
            "enable_prometheus_export": True,
            "prometheus_port": 8080,
            "prometheus_path": "/metrics",
            "otel_service_name": "testapp",
            "enable_default_metrics": True,
        }

        config = MetricConfig.from_dict(config_dict)

        assert config.enable_otel is True
        assert config.enable_prometheus_export is True
        assert config.prometheus_port == 8080
        assert config.prometheus_path == "/metrics"
        assert config.otel_service_name == "testapp"
        assert config.enable_default_metrics is True


class TestOpenTelemetryCollector:
    """Pruebas para el recolector OpenTelemetry."""

    def test_otel_collector_creation(self):
        """Prueba la creación de un recolector OpenTelemetry."""
        config = MetricConfig()
        collector = OpenTelemetryCollector(config)

        assert collector.config == config
        assert collector._initialized is False

    def test_otel_collector_initialize(self):
        """Prueba la inicialización del recolector."""
        # Deshabilitar Prometheus para evitar problemas
        config = MetricConfig(enable_otel=True, enable_prometheus_export=False)
        collector = OpenTelemetryCollector(config)

        collector.initialize()

        assert collector._initialized is True
        assert collector._meter is not None

    def test_otel_collector_create_counter(self):
        """Prueba la creación de un contador a través del recolector."""
        config = MetricConfig()
        collector = OpenTelemetryCollector(config)
        collector.initialize()

        counter = collector.counter("test_counter", "Test counter")

        # Verificar que es un contador OpenTelemetry nativo
        assert hasattr(counter, "add")
        assert callable(counter.add)

    def test_otel_collector_create_gauge(self):
        """Prueba la creación de un gauge a través del recolector."""
        config = MetricConfig()
        collector = OpenTelemetryCollector(config)
        collector.initialize()

        gauge = collector.gauge("test_gauge", "Test gauge")

        # Verificar que es un gauge OpenTelemetry nativo
        assert hasattr(gauge, "add")
        assert callable(gauge.add)

    def test_otel_collector_create_histogram(self):
        """Prueba la creación de un histograma a través del recolector."""
        config = MetricConfig()
        collector = OpenTelemetryCollector(config)
        collector.initialize()

        histogram = collector.histogram("test_histogram", "Test histogram")

        # Verificar que es un histograma OpenTelemetry nativo
        assert hasattr(histogram, "record")
        assert callable(histogram.record)


class TestMetricsIntegration:
    """Pruebas de integración para el sistema de métricas."""

    def test_create_counter_function(self):
        """Prueba la función de conveniencia create_counter."""
        config = MetricConfig()
        collector = OpenTelemetryCollector(config)
        collector.initialize()

        with patch("turboapi.observability.metrics.get_metrics_collector", return_value=collector):
            counter = create_counter("test_counter", "Test counter")

            # Verificar que es un contador OpenTelemetry nativo
            assert hasattr(counter, "add")
            assert callable(counter.add)

    def test_create_gauge_function(self):
        """Prueba la función de conveniencia create_gauge."""
        config = MetricConfig()
        collector = OpenTelemetryCollector(config)
        collector.initialize()

        with patch("turboapi.observability.metrics.get_metrics_collector", return_value=collector):
            gauge = create_gauge("test_gauge", "Test gauge")

            # Verificar que es un gauge OpenTelemetry nativo
            assert hasattr(gauge, "add")
            assert callable(gauge.add)

    def test_create_histogram_function(self):
        """Prueba la función de conveniencia create_histogram."""
        config = MetricConfig()
        collector = OpenTelemetryCollector(config)
        collector.initialize()

        with patch("turboapi.observability.metrics.get_metrics_collector", return_value=collector):
            histogram = create_histogram("test_histogram", "Test histogram")

            # Verificar que es un histograma OpenTelemetry nativo
            assert hasattr(histogram, "record")
            assert callable(histogram.record)

    def test_create_summary_function(self):
        """Prueba la función de conveniencia create_summary."""
        config = MetricConfig()
        collector = OpenTelemetryCollector(config)
        collector.initialize()

        with patch("turboapi.observability.metrics.get_metrics_collector", return_value=collector):
            summary = create_summary("test_summary", "Test summary")

            # Verificar que es un resumen OpenTelemetry nativo (implementado como histogram)
            assert hasattr(summary, "record")
            assert callable(summary.record)

    def test_get_metrics_collector_function(self):
        """Prueba la función de conveniencia get_metrics_collector."""
        # La función ahora siempre retorna una nueva instancia
        retrieved_collector = get_metrics_collector()

        assert retrieved_collector is not None
        assert isinstance(retrieved_collector, OpenTelemetryCollector)

    def test_get_metrics_collector_not_configured(self):
        """Prueba get_metrics_collector cuando no está configurado."""
        # La función ahora siempre retorna una nueva instancia, no lanza excepción
        retrieved_collector = get_metrics_collector()

        assert retrieved_collector is not None
        assert isinstance(retrieved_collector, OpenTelemetryCollector)

    def test_metrics_workflow_integration(self):
        """Prueba un flujo completo de trabajo con métricas."""
        config = MetricConfig()
        collector = OpenTelemetryCollector(config)
        collector.initialize()

        # Crear diferentes tipos de métricas usando OpenTelemetry nativo
        request_counter = collector.counter("http_requests_total", "Total HTTP requests")
        response_time_histogram = collector.histogram(
            "http_request_duration_seconds", "HTTP request duration"
        )
        active_connections_gauge = collector.gauge("active_connections", "Active connections")

        # Simular algunas operaciones usando la API nativa de OpenTelemetry
        request_counter.add(1, {"method": "GET", "status": "200"})
        request_counter.add(1, {"method": "POST", "status": "201"})

        response_time_histogram.record(0.1, {"method": "GET"})
        response_time_histogram.record(0.2, {"method": "POST"})

        active_connections_gauge.add(42, {"instance": "server1"})
        active_connections_gauge.add(5, {"instance": "server1"})

        # Verificar que las métricas tienen los métodos correctos
        assert hasattr(request_counter, "add")
        assert hasattr(response_time_histogram, "record")
        assert hasattr(active_connections_gauge, "add")
