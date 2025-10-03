"""Pruebas para los endpoints de diagnóstico."""

import time
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from turboapi.observability.diagnostics import DiagnosticsRouter
from turboapi.observability.diagnostics import create_diagnostics_router
from turboapi.observability.health import HealthCheckResponse
from turboapi.observability.health import HealthStatus


class TestDiagnosticsRouter:
    """Pruebas para DiagnosticsRouter."""

    def test_diagnostics_router_creation(self):
        """Prueba la creación de DiagnosticsRouter."""
        router = DiagnosticsRouter()

        assert router.health_checker is None
        assert router.router is not None
        assert router.logger is not None

    def test_diagnostics_router_with_health_checker(self):
        """Prueba la creación de DiagnosticsRouter con health checker."""
        mock_health_checker = MagicMock()
        router = DiagnosticsRouter(mock_health_checker)

        assert router.health_checker == mock_health_checker

    def test_diagnostics_router_routes_setup(self):
        """Prueba que las rutas se configuran correctamente."""
        router = DiagnosticsRouter()

        # Verificar que las rutas están configuradas
        routes = [route.path for route in router.router.routes]

        expected_routes = [
            "/health",
            "/health/{check_name}",
            "/ready",
            "/live",
            "/metrics",
            "/info",
            "/system",
            "/memory",
            "/gc",
            "/tracing",
        ]

        for expected_route in expected_routes:
            assert any(expected_route in route for route in routes)


class TestDiagnosticsEndpoints:
    """Pruebas para los endpoints de diagnóstico."""

    @pytest.fixture
    def app(self):
        """Crea una aplicación FastAPI para testing."""
        app = FastAPI()
        router = create_diagnostics_router()
        app.include_router(router, prefix="/diagnostics")
        return app

    @pytest.fixture
    def client(self, app):
        """Crea un cliente de prueba."""
        return TestClient(app)

    @pytest.fixture
    def mock_health_checker(self):
        """Crea un mock del health checker."""
        checker = MagicMock()
        checker.version = "1.0.0"
        checker.start_time = time.time() - 100  # 100 segundos de uptime

        # Mock response
        response = HealthCheckResponse(
            status=HealthStatus.HEALTHY,
            timestamp=time.time(),
            version="1.0.0",
            uptime_seconds=100.0,
            checks=[],
            summary={"healthy": 1, "degraded": 0, "unhealthy": 0, "unknown": 0},
        )
        checker.run_all_checks = AsyncMock(return_value=response)
        return checker

    def test_health_endpoint_success(self, client, mock_health_checker):
        """Prueba el endpoint de health check exitoso."""
        with patch(
            "turboapi.observability.diagnostics.get_health_checker",
            return_value=mock_health_checker,
        ):
            response = client.get("/diagnostics/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "uptime_seconds" in data

    def test_health_endpoint_unhealthy(self, client):
        """Prueba el endpoint de health check con estado unhealthy."""
        mock_checker = MagicMock()
        mock_checker.run_all_checks = AsyncMock(
            return_value=HealthCheckResponse(
                status=HealthStatus.UNHEALTHY,
                timestamp=time.time(),
                version="1.0.0",
                uptime_seconds=100.0,
                checks=[],
                summary={"healthy": 0, "degraded": 0, "unhealthy": 1, "unknown": 0},
            )
        )

        with patch(
            "turboapi.observability.diagnostics.get_health_checker", return_value=mock_checker
        ):
            response = client.get("/diagnostics/health")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"

    def test_health_single_endpoint_success(self, client, mock_health_checker):
        """Prueba el endpoint de health check individual exitoso."""
        from turboapi.observability.health import HealthCheckResult

        mock_result = HealthCheckResult(
            name="database",
            status=HealthStatus.HEALTHY,
            message="Database connection successful",
            details={"query": "SELECT 1"},
            response_time_ms=50.0,
            timestamp=time.time(),
        )
        mock_health_checker.run_single_check = AsyncMock(return_value=mock_result)

        with patch(
            "turboapi.observability.diagnostics.get_health_checker",
            return_value=mock_health_checker,
        ):
            response = client.get("/diagnostics/health/database")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "database"
        assert data["status"] == "healthy"

    def test_health_single_endpoint_not_found(self, client, mock_health_checker):
        """Prueba el endpoint de health check individual no encontrado."""
        mock_health_checker.run_single_check = AsyncMock(return_value=None)

        with patch(
            "turboapi.observability.diagnostics.get_health_checker",
            return_value=mock_health_checker,
        ):
            response = client.get("/diagnostics/health/nonexistent")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_ready_endpoint_success(self, client, mock_health_checker):
        """Prueba el endpoint de readiness probe exitoso."""
        with patch(
            "turboapi.observability.diagnostics.get_health_checker",
            return_value=mock_health_checker,
        ):
            response = client.get("/diagnostics/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True
        assert data["status"] == "healthy"

    def test_ready_endpoint_unhealthy(self, client):
        """Prueba el endpoint de readiness probe con estado unhealthy."""
        mock_checker = MagicMock()
        mock_checker.run_all_checks = AsyncMock(
            return_value=HealthCheckResponse(
                status=HealthStatus.UNHEALTHY,
                timestamp=time.time(),
                version="1.0.0",
                uptime_seconds=100.0,
                checks=[],
                summary={"healthy": 0, "degraded": 0, "unhealthy": 1, "unknown": 0},
            )
        )

        with patch(
            "turboapi.observability.diagnostics.get_health_checker", return_value=mock_checker
        ):
            response = client.get("/diagnostics/ready")

        assert response.status_code == 503
        data = response.json()
        assert data["ready"] is False

    def test_live_endpoint(self, client):
        """Prueba el endpoint de liveness probe."""
        with patch("psutil.Process") as mock_process:
            mock_process.return_value.create_time.return_value = time.time() - 100
            response = client.get("/diagnostics/live")

        assert response.status_code == 200
        data = response.json()
        assert data["alive"] is True
        assert "uptime" in data

    def test_metrics_endpoint(self, client):
        """Prueba el endpoint de métricas."""
        with patch("psutil.Process") as mock_process:
            mock_process.return_value.cpu_percent.return_value = 10.0
            mock_process.return_value.memory_info.return_value = MagicMock(rss=1000000, vms=2000000)
            mock_process.return_value.memory_percent.return_value = 5.0
            mock_process.return_value.num_threads.return_value = 4
            mock_process.return_value.num_fds.return_value = 10

            with patch("psutil.virtual_memory") as mock_virtual_memory:
                mock_virtual_memory.return_value.total = 8000000000
                mock_virtual_memory.return_value.available = 4000000000
                mock_virtual_memory.return_value.percent = 50.0
                mock_virtual_memory.return_value.used = 4000000000

                with patch(
                    "turboapi.observability.diagnostics.get_metrics_collector"
                ) as mock_get_collector:
                    mock_get_collector.side_effect = RuntimeError("Not configured")
                    response = client.get("/diagnostics/metrics")

        assert response.status_code == 200
        data = response.json()
        assert "system" in data
        assert "python" in data
        assert data["application"]["metrics_collector_initialized"] is False

    def test_info_endpoint(self, client, mock_health_checker):
        """Prueba el endpoint de información."""
        with patch(
            "turboapi.observability.diagnostics.get_health_checker",
            return_value=mock_health_checker,
        ):
            response = client.get("/diagnostics/info")

        assert response.status_code == 200
        data = response.json()
        assert data["application"]["name"] == "TurboAPI"
        assert data["application"]["version"] == "1.0.0"
        assert "environment" in data
        assert "dependencies" in data

    def test_system_endpoint(self, client):
        """Prueba el endpoint de información del sistema."""
        with patch("platform.node", return_value="test-host"):
            with patch("platform.platform", return_value="Windows-10"):
                with patch("platform.architecture", return_value=("64bit", "WindowsPE")):
                    with patch("platform.processor", return_value="Intel64"):
                        with patch("psutil.cpu_count", return_value=4):
                            with patch("psutil.cpu_percent", return_value=10.0):
                                with patch("psutil.cpu_freq", return_value=None):
                                    with patch("psutil.virtual_memory") as mock_virtual_memory:
                                        mock_virtual_memory.return_value.total = 8000000000
                                        mock_virtual_memory.return_value.available = 4000000000
                                        mock_virtual_memory.return_value.percent = 50.0
                                        mock_virtual_memory.return_value.used = 4000000000

                                        with patch("psutil.disk_usage") as mock_disk_usage:
                                            mock_disk_usage.return_value.total = 100000000000
                                            mock_disk_usage.return_value.used = 50000000000
                                            mock_disk_usage.return_value.free = 50000000000
                                            mock_disk_usage.return_value.percent = 50.0

                                            response = client.get("/diagnostics/system")

        assert response.status_code == 200
        data = response.json()
        assert data["system"]["hostname"] == "test-host"
        assert "cpu" in data
        assert "memory" in data
        assert "disk" in data

    def test_memory_endpoint(self, client):
        """Prueba el endpoint de información de memoria."""
        with patch("psutil.Process") as mock_process:
            mock_process.return_value.pid = 1234
            mock_process.return_value.memory_info.return_value = MagicMock(rss=1000000, vms=2000000)
            mock_process.return_value.memory_percent.return_value = 5.0
            mock_process.return_value.num_threads.return_value = 4

            with patch("psutil.virtual_memory") as mock_virtual_memory:
                mock_virtual_memory.return_value.total = 8000000000
                mock_virtual_memory.return_value.available = 4000000000
                mock_virtual_memory.return_value.percent = 50.0
                mock_virtual_memory.return_value.used = 4000000000

                response = client.get("/diagnostics/memory")

        assert response.status_code == 200
        data = response.json()
        assert data["process"]["pid"] == 1234
        assert "memory" in data["process"]
        assert "system" in data
        assert "python" in data

    def test_gc_endpoint(self, client):
        """Prueba el endpoint de garbage collection."""
        with patch("psutil.Process") as mock_process:
            mock_before_memory = MagicMock(rss=1000000, vms=2000000)
            mock_after_memory = MagicMock(rss=800000, vms=1800000)
            mock_process.return_value.memory_info.side_effect = [
                mock_before_memory,
                mock_after_memory,
            ]

            with patch("gc.get_count", side_effect=[[10, 5, 2], [8, 3, 1]]):
                with patch("gc.collect", return_value=5):
                    response = client.post("/diagnostics/gc")

        assert response.status_code == 200
        data = response.json()
        assert data["garbage_collection"]["collected_objects"] == 5
        assert data["garbage_collection"]["memory_freed"] == 200000
        assert "before" in data["garbage_collection"]
        assert "after" in data["garbage_collection"]

    def test_tracing_endpoint_not_configured(self, client):
        """Prueba el endpoint de información de tracing no configurado."""
        with patch("turboapi.observability.diagnostics.get_tracer") as mock_get_tracer:
            mock_get_tracer.side_effect = RuntimeError("Tracing not configured")
            response = client.get("/diagnostics/tracing")

        assert response.status_code == 200
        data = response.json()
        assert data["tracing"]["enabled"] is False

    def test_tracing_endpoint_configured(self, client):
        """Prueba el endpoint de información de tracing configurado."""
        mock_tracer = MagicMock()
        mock_tracer.config.service_name = "test-service"
        mock_tracer.config.enable_jaeger = True
        mock_tracer.config.enable_otlp = False
        mock_tracer.config.enable_auto_instrumentation = True

        with patch("turboapi.observability.diagnostics.get_tracer", return_value=mock_tracer):
            response = client.get("/diagnostics/tracing")

        assert response.status_code == 200
        data = response.json()
        assert data["tracing"]["enabled"] is True
        assert data["tracing"]["provider"] == "OpenTelemetry"
        assert data["tracing"]["service_name"] == "test-service"
        assert data["tracing"]["jaeger_enabled"] is True
        assert data["tracing"]["otlp_enabled"] is False


class TestCreateDiagnosticsRouter:
    """Pruebas para la función create_diagnostics_router."""

    def test_create_diagnostics_router_default(self):
        """Prueba la creación de router de diagnóstico por defecto."""
        router = create_diagnostics_router()

        assert router is not None
        assert hasattr(router, "routes")

    def test_create_diagnostics_router_with_health_checker(self):
        """Prueba la creación de router de diagnóstico con health checker."""
        mock_health_checker = MagicMock()
        router = create_diagnostics_router(mock_health_checker)

        assert router is not None
        assert hasattr(router, "routes")
