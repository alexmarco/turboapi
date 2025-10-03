"""Sistema de health checks y endpoints de diagnóstico para TurboAPI."""

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from pydantic import BaseModel


class HealthStatus(str, Enum):
    """Estados de salud del sistema."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Resultado de un health check individual."""

    name: str
    status: HealthStatus
    message: str
    details: dict[str, Any]
    response_time_ms: float
    timestamp: float

    def to_dict(self) -> dict[str, Any]:
        """
        Convierte el resultado a diccionario.

        Returns
        -------
        Dict[str, Any]
            Diccionario con los datos del health check.
        """
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "response_time_ms": self.response_time_ms,
            "timestamp": self.timestamp,
        }


class HealthCheckResponse(BaseModel):
    """Respuesta del sistema de health checks."""

    status: HealthStatus
    timestamp: float
    version: str
    uptime_seconds: float
    checks: list[dict[str, Any]]
    summary: dict[str, int]

    class Config:
        """Configuración de Pydantic."""

        use_enum_values = True


class BaseHealthCheck:
    """Clase base para health checks."""

    def __init__(self, name: str, timeout: float = 5.0):
        """
        Inicializa un health check.

        Parameters
        ----------
        name : str
            Nombre del health check.
        timeout : float, optional
            Timeout en segundos (default: 5.0).

        Examples
        --------
        >>> class DatabaseHealthCheck(BaseHealthCheck):
        ...     def __init__(self):
        ...         super().__init__("database")
        ...
        ...     async def check(self) -> HealthCheckResult:
        ...         # Implementar verificación de base de datos
        ...         pass
        """
        self.name = name
        self.timeout = timeout

    async def check(self) -> HealthCheckResult:
        """
        Ejecuta el health check.

        Returns
        -------
        HealthCheckResult
            Resultado del health check.

        Raises
        ------
        NotImplementedError
            Si no se implementa el método.
        """
        raise NotImplementedError("Subclasses must implement check() method")

    async def _run_with_timeout(self) -> HealthCheckResult:
        """
        Ejecuta el health check con timeout.

        Returns
        -------
        HealthCheckResult
            Resultado del health check.

        Raises
        ------
        asyncio.TimeoutError
            Si el health check excede el timeout.
        """
        try:
            return await asyncio.wait_for(self.check(), timeout=self.timeout)
        except asyncio.TimeoutError:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check timed out after {self.timeout}s",
                details={"timeout": self.timeout},
                response_time_ms=self.timeout * 1000,
                timestamp=time.time(),
            )
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                details={"error": str(e), "error_type": type(e).__name__},
                response_time_ms=0.0,
                timestamp=time.time(),
            )


class DatabaseHealthCheck(BaseHealthCheck):
    """Health check para base de datos."""

    def __init__(self, engine: Any, timeout: float = 5.0):
        """
        Inicializa el health check de base de datos.

        Parameters
        ----------
        engine : Any
            Motor de base de datos (SQLAlchemy Engine).
        timeout : float, optional
            Timeout en segundos (default: 5.0).

        Examples
        --------
        >>> from sqlalchemy import create_engine
        >>> engine = create_engine("sqlite:///test.db")
        >>> db_check = DatabaseHealthCheck(engine)
        """
        super().__init__("database", timeout)
        self.engine = engine

    async def check(self) -> HealthCheckResult:
        """
        Verifica la conectividad de la base de datos.

        Returns
        -------
        HealthCheckResult
            Resultado del health check de base de datos.
        """
        start_time = time.time()

        try:
            # Ejecutar una consulta simple
            with self.engine.connect() as connection:
                result = connection.execute("SELECT 1")
                result.fetchone()

            response_time = (time.time() - start_time) * 1000

            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Database connection successful",
                details={
                    "query": "SELECT 1",
                    "connection_pool_size": getattr(self.engine.pool, "size", "unknown"),
                },
                response_time_ms=response_time,
                timestamp=time.time(),
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}",
                details={"error": str(e), "error_type": type(e).__name__},
                response_time_ms=response_time,
                timestamp=time.time(),
            )


class RedisHealthCheck(BaseHealthCheck):
    """Health check para Redis."""

    def __init__(self, redis_client: Any, timeout: float = 5.0):
        """
        Inicializa el health check de Redis.

        Parameters
        ----------
        redis_client : Any
            Cliente de Redis.
        timeout : float, optional
            Timeout en segundos (default: 5.0).

        Examples
        --------
        >>> import redis
        >>> redis_client = redis.Redis(host='localhost', port=6379)
        >>> redis_check = RedisHealthCheck(redis_client)
        """
        super().__init__("redis", timeout)
        self.redis_client = redis_client

    async def check(self) -> HealthCheckResult:
        """
        Verifica la conectividad de Redis.

        Returns
        -------
        HealthCheckResult
            Resultado del health check de Redis.
        """
        start_time = time.time()

        try:
            # Ejecutar comando PING
            result = await asyncio.get_event_loop().run_in_executor(None, self.redis_client.ping)

            response_time = (time.time() - start_time) * 1000

            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Redis connection successful",
                details={"ping_result": result},
                response_time_ms=response_time,
                timestamp=time.time(),
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Redis connection failed: {str(e)}",
                details={"error": str(e), "error_type": type(e).__name__},
                response_time_ms=response_time,
                timestamp=time.time(),
            )


class ExternalServiceHealthCheck(BaseHealthCheck):
    """Health check para servicios externos."""

    def __init__(self, name: str, check_func: Callable[[], Any], timeout: float = 5.0):
        """
        Inicializa el health check de servicio externo.

        Parameters
        ----------
        name : str
            Nombre del servicio.
        check_func : Callable[[], Any]
            Función que verifica el servicio.
        timeout : float, optional
            Timeout en segundos (default: 5.0).

        Examples
        --------
        >>> async def check_api():
        ...     # Verificar API externa
        ...     return True
        >>> api_check = ExternalServiceHealthCheck("external_api", check_api)
        """
        super().__init__(name, timeout)
        self.check_func = check_func

    async def check(self) -> HealthCheckResult:
        """
        Verifica el servicio externo.

        Returns
        -------
        HealthCheckResult
            Resultado del health check del servicio externo.
        """
        start_time = time.time()

        try:
            result = await self.check_func()
            response_time = (time.time() - start_time) * 1000

            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="External service is available",
                details={"result": result},
                response_time_ms=response_time,
                timestamp=time.time(),
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"External service check failed: {str(e)}",
                details={"error": str(e), "error_type": type(e).__name__},
                response_time_ms=response_time,
                timestamp=time.time(),
            )


class HealthChecker:
    """Gestor de health checks."""

    def __init__(self, version: str = "0.1.0"):
        """
        Inicializa el gestor de health checks.

        Parameters
        ----------
        version : str, optional
            Versión de la aplicación (default: "0.1.0").

        Examples
        --------
        >>> health_checker = HealthChecker("1.0.0")
        >>> health_checker.add_check(DatabaseHealthCheck(engine))
        """
        self.version = version
        self.checks: list[BaseHealthCheck] = []
        self.start_time = time.time()

    def add_check(self, check: BaseHealthCheck) -> None:
        """
        Añade un health check.

        Parameters
        ----------
        check : BaseHealthCheck
            Health check a añadir.

        Examples
        --------
        >>> health_checker.add_check(DatabaseHealthCheck(engine))
        """
        self.checks.append(check)

    def remove_check(self, name: str) -> None:
        """
        Elimina un health check por nombre.

        Parameters
        ----------
        name : str
            Nombre del health check a eliminar.

        Examples
        --------
        >>> health_checker.remove_check("database")
        """
        self.checks = [check for check in self.checks if check.name != name]

    async def run_all_checks(self) -> HealthCheckResponse:
        """
        Ejecuta todos los health checks.

        Returns
        -------
        HealthCheckResponse
            Respuesta con todos los health checks.

        Examples
        --------
        >>> response = await health_checker.run_all_checks()
        >>> print(response.status)
        """
        if not self.checks:
            return HealthCheckResponse(
                status=HealthStatus.HEALTHY,
                timestamp=time.time(),
                version=self.version,
                uptime_seconds=time.time() - self.start_time,
                checks=[],
                summary={"healthy": 0, "degraded": 0, "unhealthy": 0, "unknown": 0},
            )

        # Ejecutar todos los checks en paralelo
        tasks = [check._run_with_timeout() for check in self.checks]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Procesar resultados
        check_results = []
        summary = {"healthy": 0, "degraded": 0, "unhealthy": 0, "unknown": 0}

        for result in results:
            if isinstance(result, Exception):
                error_result = HealthCheckResult(
                    name="unknown",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check failed with exception: {str(result)}",
                    details={"error": str(result), "error_type": type(result).__name__},
                    response_time_ms=0.0,
                    timestamp=time.time(),
                )
                check_results.append(error_result.to_dict())
                summary["unhealthy"] += 1
            else:
                # result es HealthCheckResult (verificado por isinstance)
                assert isinstance(result, HealthCheckResult)
                check_results.append(result.to_dict())
                summary[result.status.value] += 1

        # Determinar estado general
        if summary["unhealthy"] > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif summary["degraded"] > 0:
            overall_status = HealthStatus.DEGRADED
        elif summary["healthy"] > 0:
            overall_status = HealthStatus.HEALTHY
        else:
            overall_status = HealthStatus.UNKNOWN

        return HealthCheckResponse(
            status=overall_status,
            timestamp=time.time(),
            version=self.version,
            uptime_seconds=time.time() - self.start_time,
            checks=check_results,
            summary=summary,
        )

    async def run_single_check(self, name: str) -> HealthCheckResult | None:
        """
        Ejecuta un health check específico.

        Parameters
        ----------
        name : str
            Nombre del health check a ejecutar.

        Returns
        -------
        Optional[HealthCheckResult]
            Resultado del health check o None si no se encuentra.

        Examples
        --------
        >>> result = await health_checker.run_single_check("database")
        >>> if result:
        ...     print(result.status)
        """
        for check in self.checks:
            if check.name == name:
                return await check._run_with_timeout()
        return None


# Funciones de conveniencia para compatibilidad con código existente
# Estas funciones están deprecadas y se recomienda usar inyección de dependencias


def configure_health_checks(version: str = "0.1.0") -> HealthChecker:
    """
    Configura el sistema de health checks.

    Parameters
    ----------
    version : str, optional
        Versión de la aplicación (default: "0.1.0").

    Returns
    -------
    HealthChecker
        Instancia del health checker configurado.

    Examples
    --------
    >>> health_checker = configure_health_checks("1.0.0")
    >>> health_checker.add_check(DatabaseHealthCheck(engine))

    Note
    ----
    Esta función está deprecada. Se recomienda usar inyección de dependencias
    a través del contenedor DI del framework.
    """
    return HealthChecker(version)


def get_health_checker() -> HealthChecker:
    """
    Obtiene una nueva instancia del health checker.

    Returns
    -------
    HealthChecker
        Nueva instancia del health checker.

    Examples
    --------
    >>> health_checker = get_health_checker()
    >>> response = await health_checker.run_all_checks()

    Note
    ----
    Esta función está deprecada. Se recomienda usar inyección de dependencias
    a través del contenedor DI del framework.
    """
    return HealthChecker()
