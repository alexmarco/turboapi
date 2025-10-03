"""Pruebas para el sistema de health checks."""

import asyncio
import time
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from turboapi.observability.health import BaseHealthCheck
from turboapi.observability.health import DatabaseHealthCheck
from turboapi.observability.health import ExternalServiceHealthCheck
from turboapi.observability.health import HealthChecker
from turboapi.observability.health import HealthCheckResult
from turboapi.observability.health import HealthStatus
from turboapi.observability.health import RedisHealthCheck
from turboapi.observability.health import configure_health_checks
from turboapi.observability.health import get_health_checker


class TestHealthStatus:
    """Pruebas para HealthStatus."""

    def test_health_status_values(self):
        """Prueba los valores de HealthStatus."""
        assert HealthStatus.HEALTHY == "healthy"
        assert HealthStatus.DEGRADED == "degraded"
        assert HealthStatus.UNHEALTHY == "unhealthy"
        assert HealthStatus.UNKNOWN == "unknown"


class TestHealthCheckResult:
    """Pruebas para HealthCheckResult."""

    def test_health_check_result_creation(self):
        """Prueba la creación de HealthCheckResult."""
        result = HealthCheckResult(
            name="test_check",
            status=HealthStatus.HEALTHY,
            message="Test successful",
            details={"key": "value"},
            response_time_ms=100.0,
            timestamp=time.time(),
        )

        assert result.name == "test_check"
        assert result.status == HealthStatus.HEALTHY
        assert result.message == "Test successful"
        assert result.details == {"key": "value"}
        assert result.response_time_ms == 100.0
        assert isinstance(result.timestamp, float)

    def test_health_check_result_to_dict(self):
        """Prueba la conversión a diccionario."""
        result = HealthCheckResult(
            name="test_check",
            status=HealthStatus.HEALTHY,
            message="Test successful",
            details={"key": "value"},
            response_time_ms=100.0,
            timestamp=1234567890.0,
        )

        result_dict = result.to_dict()

        assert result_dict == {
            "name": "test_check",
            "status": "healthy",
            "message": "Test successful",
            "details": {"key": "value"},
            "response_time_ms": 100.0,
            "timestamp": 1234567890.0,
        }


class TestBaseHealthCheck:
    """Pruebas para BaseHealthCheck."""

    def test_base_health_check_creation(self):
        """Prueba la creación de BaseHealthCheck."""
        check = BaseHealthCheck("test_check", timeout=10.0)

        assert check.name == "test_check"
        assert check.timeout == 10.0

    def test_base_health_check_default_timeout(self):
        """Prueba el timeout por defecto."""
        check = BaseHealthCheck("test_check")

        assert check.timeout == 5.0

    async def test_base_health_check_not_implemented(self):
        """Prueba que check() lanza NotImplementedError."""
        check = BaseHealthCheck("test_check")

        with pytest.raises(NotImplementedError):
            await check.check()

    async def test_base_health_check_timeout(self):
        """Prueba el manejo de timeout."""

        class SlowHealthCheck(BaseHealthCheck):
            async def check(self):
                await asyncio.sleep(10)  # Más largo que el timeout
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    message="Success",
                    details={},
                    response_time_ms=0.0,
                    timestamp=time.time(),
                )

        check = SlowHealthCheck("slow_check", timeout=0.1)
        result = await check._run_with_timeout()

        assert result.status == HealthStatus.UNHEALTHY
        assert "timed out" in result.message
        assert result.response_time_ms == 100.0  # 0.1s * 1000

    async def test_base_health_check_exception(self):
        """Prueba el manejo de excepciones."""

        class FailingHealthCheck(BaseHealthCheck):
            async def check(self):
                raise ValueError("Test error")

        check = FailingHealthCheck("failing_check")
        result = await check._run_with_timeout()

        assert result.status == HealthStatus.UNHEALTHY
        assert "Test error" in result.message
        assert result.details["error"] == "Test error"
        assert result.details["error_type"] == "ValueError"


class TestDatabaseHealthCheck:
    """Pruebas para DatabaseHealthCheck."""

    def test_database_health_check_creation(self):
        """Prueba la creación de DatabaseHealthCheck."""
        mock_engine = MagicMock()
        check = DatabaseHealthCheck(mock_engine)

        assert check.name == "database"
        assert check.engine == mock_engine

    async def test_database_health_check_success(self):
        """Prueba un health check de base de datos exitoso."""
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (1,)

        mock_connection.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        check = DatabaseHealthCheck(mock_engine)
        result = await check.check()

        assert result.status == HealthStatus.HEALTHY
        assert "successful" in result.message
        assert "SELECT 1" in result.details["query"]
        assert result.response_time_ms >= 0  # Puede ser 0 en tests rápidos

    async def test_database_health_check_failure(self):
        """Prueba un health check de base de datos fallido."""
        mock_engine = MagicMock()
        mock_engine.connect.side_effect = Exception("Connection failed")

        check = DatabaseHealthCheck(mock_engine)
        result = await check.check()

        assert result.status == HealthStatus.UNHEALTHY
        assert "failed" in result.message
        assert result.details["error"] == "Connection failed"


class TestRedisHealthCheck:
    """Pruebas para RedisHealthCheck."""

    def test_redis_health_check_creation(self):
        """Prueba la creación de RedisHealthCheck."""
        mock_redis = MagicMock()
        check = RedisHealthCheck(mock_redis)

        assert check.name == "redis"
        assert check.redis_client == mock_redis

    async def test_redis_health_check_success(self):
        """Prueba un health check de Redis exitoso."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True

        check = RedisHealthCheck(mock_redis)

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = AsyncMock(return_value=True)
            result = await check.check()

        assert result.status == HealthStatus.HEALTHY
        assert "successful" in result.message
        assert result.details["ping_result"] is True

    async def test_redis_health_check_failure(self):
        """Prueba un health check de Redis fallido."""
        mock_redis = MagicMock()
        mock_redis.ping.side_effect = Exception("Redis connection failed")

        check = RedisHealthCheck(mock_redis)

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = AsyncMock(
                side_effect=Exception("Redis connection failed")
            )
            result = await check.check()

        assert result.status == HealthStatus.UNHEALTHY
        assert "failed" in result.message
        assert result.details["error"] == "Redis connection failed"


class TestExternalServiceHealthCheck:
    """Pruebas para ExternalServiceHealthCheck."""

    def test_external_service_health_check_creation(self):
        """Prueba la creación de ExternalServiceHealthCheck."""

        async def check_func():
            return True

        check = ExternalServiceHealthCheck("external_api", check_func)

        assert check.name == "external_api"
        assert check.check_func == check_func

    async def test_external_service_health_check_success(self):
        """Prueba un health check de servicio externo exitoso."""

        async def check_func():
            return {"status": "ok"}

        check = ExternalServiceHealthCheck("external_api", check_func)
        result = await check.check()

        assert result.status == HealthStatus.HEALTHY
        assert "available" in result.message
        assert result.details["result"] == {"status": "ok"}

    async def test_external_service_health_check_failure(self):
        """Prueba un health check de servicio externo fallido."""

        async def check_func():
            raise Exception("Service unavailable")

        check = ExternalServiceHealthCheck("external_api", check_func)
        result = await check.check()

        assert result.status == HealthStatus.UNHEALTHY
        assert "failed" in result.message
        assert result.details["error"] == "Service unavailable"


class TestHealthChecker:
    """Pruebas para HealthChecker."""

    def test_health_checker_creation(self):
        """Prueba la creación de HealthChecker."""
        checker = HealthChecker("1.0.0")

        assert checker.version == "1.0.0"
        assert checker.checks == []
        assert checker.start_time > 0

    def test_health_checker_add_check(self):
        """Prueba añadir un health check."""
        checker = HealthChecker()
        mock_check = MagicMock()
        mock_check.name = "test_check"

        checker.add_check(mock_check)

        assert len(checker.checks) == 1
        assert checker.checks[0] == mock_check

    def test_health_checker_remove_check(self):
        """Prueba eliminar un health check."""
        checker = HealthChecker()
        mock_check1 = MagicMock()
        mock_check1.name = "check1"
        mock_check2 = MagicMock()
        mock_check2.name = "check2"

        checker.add_check(mock_check1)
        checker.add_check(mock_check2)
        checker.remove_check("check1")

        assert len(checker.checks) == 1
        assert checker.checks[0] == mock_check2

    async def test_health_checker_run_all_checks_empty(self):
        """Prueba ejecutar todos los checks cuando no hay ninguno."""
        checker = HealthChecker("1.0.0")
        response = await checker.run_all_checks()

        assert response.status == HealthStatus.HEALTHY
        assert response.version == "1.0.0"
        assert response.checks == []
        assert response.summary == {"healthy": 0, "degraded": 0, "unhealthy": 0, "unknown": 0}

    async def test_health_checker_run_all_checks_success(self):
        """Prueba ejecutar todos los checks exitosamente."""
        checker = HealthChecker("1.0.0")

        # Mock health check que siempre pasa
        mock_check = MagicMock()
        mock_check._run_with_timeout = AsyncMock(
            return_value=HealthCheckResult(
                name="test_check",
                status=HealthStatus.HEALTHY,
                message="Success",
                details={},
                response_time_ms=100.0,
                timestamp=time.time(),
            )
        )

        checker.add_check(mock_check)
        response = await checker.run_all_checks()

        assert response.status == HealthStatus.HEALTHY
        assert len(response.checks) == 1
        assert response.summary["healthy"] == 1

    async def test_health_checker_run_all_checks_failure(self):
        """Prueba ejecutar todos los checks con fallos."""
        checker = HealthChecker("1.0.0")

        # Mock health check que falla
        mock_check = MagicMock()
        mock_check._run_with_timeout = AsyncMock(
            return_value=HealthCheckResult(
                name="test_check",
                status=HealthStatus.UNHEALTHY,
                message="Failed",
                details={},
                response_time_ms=50.0,
                timestamp=time.time(),
            )
        )

        checker.add_check(mock_check)
        response = await checker.run_all_checks()

        assert response.status == HealthStatus.UNHEALTHY
        assert len(response.checks) == 1
        assert response.summary["unhealthy"] == 1

    async def test_health_checker_run_all_checks_mixed(self):
        """Prueba ejecutar checks con resultados mixtos."""
        checker = HealthChecker("1.0.0")

        # Mock health check saludable
        healthy_check = MagicMock()
        healthy_check._run_with_timeout = AsyncMock(
            return_value=HealthCheckResult(
                name="healthy_check",
                status=HealthStatus.HEALTHY,
                message="Success",
                details={},
                response_time_ms=100.0,
                timestamp=time.time(),
            )
        )

        # Mock health check degradado
        degraded_check = MagicMock()
        degraded_check._run_with_timeout = AsyncMock(
            return_value=HealthCheckResult(
                name="degraded_check",
                status=HealthStatus.DEGRADED,
                message="Degraded",
                details={},
                response_time_ms=200.0,
                timestamp=time.time(),
            )
        )

        checker.add_check(healthy_check)
        checker.add_check(degraded_check)
        response = await checker.run_all_checks()

        assert response.status == HealthStatus.DEGRADED
        assert len(response.checks) == 2
        assert response.summary["healthy"] == 1
        assert response.summary["degraded"] == 1

    async def test_health_checker_run_single_check(self):
        """Prueba ejecutar un check individual."""
        checker = HealthChecker("1.0.0")

        mock_check = MagicMock()
        mock_check.name = "test_check"
        mock_check._run_with_timeout = AsyncMock(
            return_value=HealthCheckResult(
                name="test_check",
                status=HealthStatus.HEALTHY,
                message="Success",
                details={},
                response_time_ms=100.0,
                timestamp=time.time(),
            )
        )

        checker.add_check(mock_check)
        result = await checker.run_single_check("test_check")

        assert result is not None
        assert result.status == HealthStatus.HEALTHY

    async def test_health_checker_run_single_check_not_found(self):
        """Prueba ejecutar un check individual que no existe."""
        checker = HealthChecker("1.0.0")
        result = await checker.run_single_check("nonexistent")

        assert result is None


class TestHealthCheckerIntegration:
    """Pruebas de integración para HealthChecker."""

    def test_configure_health_checks_function(self):
        """Prueba la función de conveniencia configure_health_checks."""
        checker = configure_health_checks("2.0.0")

        assert isinstance(checker, HealthChecker)
        assert checker.version == "2.0.0"

    def test_get_health_checker_function(self):
        """Prueba la función de conveniencia get_health_checker."""
        checker = get_health_checker()

        assert isinstance(checker, HealthChecker)
        assert checker.version == "0.1.0"  # Valor por defecto

    def test_get_health_checker_not_configured(self):
        """Prueba get_health_checker (ya no usa variables globales)."""
        # Ahora get_health_checker() siempre devuelve una nueva instancia
        checker = get_health_checker()
        assert isinstance(checker, HealthChecker)

    async def test_health_checker_workflow_integration(self):
        """Prueba un flujo completo de trabajo con health checks."""
        # Configurar health checker
        checker = configure_health_checks("1.0.0")

        # Añadir checks mock
        mock_db_check = MagicMock()
        mock_db_check.name = "database"
        mock_db_check._run_with_timeout = AsyncMock(
            return_value=HealthCheckResult(
                name="database",
                status=HealthStatus.HEALTHY,
                message="Database connection successful",
                details={"query": "SELECT 1"},
                response_time_ms=50.0,
                timestamp=time.time(),
            )
        )

        mock_redis_check = MagicMock()
        mock_redis_check.name = "redis"
        mock_redis_check._run_with_timeout = AsyncMock(
            return_value=HealthCheckResult(
                name="redis",
                status=HealthStatus.HEALTHY,
                message="Redis connection successful",
                details={"ping_result": True},
                response_time_ms=25.0,
                timestamp=time.time(),
            )
        )

        checker.add_check(mock_db_check)
        checker.add_check(mock_redis_check)

        # Ejecutar todos los checks
        response = await checker.run_all_checks()

        assert response.status == HealthStatus.HEALTHY
        assert len(response.checks) == 2
        assert response.summary["healthy"] == 2
        assert response.version == "1.0.0"
        assert response.uptime_seconds >= 0

        # Ejecutar check individual
        db_result = await checker.run_single_check("database")
        assert db_result is not None
        assert db_result.status == HealthStatus.HEALTHY
        assert db_result.name == "database"
