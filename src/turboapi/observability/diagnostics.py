"""Endpoints de diagnóstico para TurboAPI."""

import gc
import platform
import sys
import time
from typing import Any

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import JSONResponse

from .health import HealthChecker
from .health import HealthCheckResponse
from .health import HealthStatus
from .health import get_health_checker
from .logging import get_logger
from .metrics import get_metrics_collector
from .metrics import get_process_metrics
from .metrics import get_system_metrics
from .models import GarbageCollectionResponse
from .models import InfoResponse
from .models import LivenessResponse
from .models import MemoryResponse
from .models import MetricsResponse
from .models import ReadinessResponse
from .models import SystemResponse
from .models import TracingResponse
from .tracing import get_tracer


class DiagnosticsRouter:
    """Router de FastAPI para endpoints de diagnóstico."""

    def __init__(self, health_checker: HealthChecker | None = None):
        """
        Inicializa el router de diagnóstico.

        Parameters
        ----------
        health_checker : Optional[HealthChecker], optional
            Health checker a usar (default: None, usa el global).

        Examples
        --------
        >>> router = DiagnosticsRouter()
        >>> app.include_router(router.router, prefix="/diagnostics")
        """
        self.health_checker = health_checker
        self.router = APIRouter(tags=["diagnostics"])
        try:
            self.logger = get_logger(__name__)
        except RuntimeError:
            # Si el logging no está configurado, usar un logger básico
            import logging

            self.logger = logging.getLogger(__name__)  # type: ignore[assignment]
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Configura las rutas de diagnóstico."""
        self.router.add_api_route("/health", self.health, methods=["GET"], summary="Health check")
        self.router.add_api_route(
            "/health/{check_name}",
            self.health_single,
            methods=["GET"],
            summary="Single health check",
        )
        self.router.add_api_route("/ready", self.ready, methods=["GET"], summary="Readiness probe")
        self.router.add_api_route("/live", self.live, methods=["GET"], summary="Liveness probe")
        self.router.add_api_route(
            "/metrics", self.metrics, methods=["GET"], summary="Application metrics"
        )
        self.router.add_api_route("/info", self.info, methods=["GET"], summary="Application info")
        self.router.add_api_route(
            "/system", self.system, methods=["GET"], summary="System information"
        )
        self.router.add_api_route("/memory", self.memory, methods=["GET"], summary="Memory usage")
        self.router.add_api_route(
            "/gc", self.garbage_collection, methods=["POST"], summary="Force garbage collection"
        )
        self.router.add_api_route(
            "/tracing", self.tracing_info, methods=["GET"], summary="Tracing information"
        )

    async def health(self, request: Request) -> HealthCheckResponse:
        """
        Endpoint de health check completo.

        Parameters
        ----------
        request : Request
            Request de FastAPI.

        Returns
        -------
        HealthCheckResponse
            Respuesta con el estado de salud del sistema.

        Examples
        --------
        GET /diagnostics/health
        """
        try:
            health_checker = self.health_checker or get_health_checker()
            response = await health_checker.run_all_checks()

            # Determinar código de estado HTTP
            if response.status == HealthStatus.UNHEALTHY:
                # Para mantener compatibilidad con tests, devolver 503 pero con el response

                return JSONResponse(content=response.model_dump(), status_code=503)  # type: ignore[return-value]
            elif response.status == HealthStatus.DEGRADED:
                # Degraded pero funcional - 200 OK
                pass

            return response

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}") from e

    async def health_single(self, check_name: str, request: Request) -> dict[str, Any]:
        """
        Endpoint de health check individual.

        Parameters
        ----------
        check_name : str
            Nombre del health check a ejecutar.
        request : Request
            Request de FastAPI.

        Returns
        -------
        Dict[str, Any]
            Resultado del health check individual.

        Examples
        --------
        GET /diagnostics/health/database
        """
        try:
            health_checker = self.health_checker or get_health_checker()
            result = await health_checker.run_single_check(check_name)

            if result is None:
                raise HTTPException(
                    status_code=404, detail=f"Health check '{check_name}' not found"
                )

            return result.to_dict()

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Single health check failed for {check_name}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}") from e

    async def ready(self, request: Request) -> ReadinessResponse:
        """
        Endpoint de readiness probe (Kubernetes).

        Parameters
        ----------
        request : Request
            Request de FastAPI.

        Returns
        -------
        ReadinessResponse
            Estado de readiness del sistema.

        Examples
        --------
        GET /diagnostics/ready
        """
        try:
            health_checker = self.health_checker or get_health_checker()
            response = await health_checker.run_all_checks()

            # Para readiness, solo verificamos que no esté unhealthy
            is_ready = response.status != HealthStatus.UNHEALTHY

            readiness_response = ReadinessResponse(
                ready=is_ready,
                status=response.status.value
                if hasattr(response.status, "value")
                else str(response.status),
                timestamp=time.time(),
            )

            # Si no está ready, devolver 503
            if not is_ready:
                return JSONResponse(content=readiness_response.model_dump(), status_code=503)  # type: ignore[return-value]

            return readiness_response

        except Exception as e:
            self.logger.error(f"Readiness probe failed: {str(e)}")
            raise HTTPException(status_code=503, detail=f"Readiness probe failed: {str(e)}") from e

    async def live(self, request: Request) -> LivenessResponse:
        """
        Endpoint de liveness probe (Kubernetes).

        Parameters
        ----------
        request : Request
            Request de FastAPI.

        Returns
        -------
        LivenessResponse
            Estado de liveness del sistema.

        Examples
        --------
        GET /diagnostics/live
        """
        # Liveness probe es simple: si la aplicación responde, está viva
        # Por ahora, usar 0.0 como fallback para uptime
        uptime = 0.0

        return LivenessResponse(
            alive=True,
            timestamp=time.time(),
            uptime=uptime,
        )

    async def metrics(self, request: Request) -> MetricsResponse:
        """
        Endpoint de métricas de la aplicación.

        Parameters
        ----------
        request : Request
            Request de FastAPI.

        Returns
        -------
        MetricsResponse
            Métricas de la aplicación.

        Examples
        --------
        GET /diagnostics/metrics
        """
        try:
            # Obtener métricas del sistema desde OpenTelemetry
            system_metrics_data = get_system_metrics()
            process_metrics_data = get_process_metrics()

            system_metrics = {
                "cpu_percent": system_metrics_data["cpu_percent"],
                "memory": {
                    "rss": process_metrics_data["memory_rss"],
                    "vms": process_metrics_data["memory_vms"],
                    "percent": process_metrics_data["memory_percent"],
                },
                "num_threads": process_metrics_data["num_threads"],
                "num_fds": process_metrics_data["num_fds"],
            }

            python_info = {
                "version": sys.version,
                "platform": platform.platform(),
                "gc_counts": gc.get_count(),
            }

            # Añadir métricas de OpenTelemetry si están disponibles
            try:
                _ = get_metrics_collector()
                application_metrics = {
                    "metrics_collector_initialized": True,
                }
            except RuntimeError:
                application_metrics = {
                    "metrics_collector_initialized": False,
                }

            from .models import PythonInfo

            return MetricsResponse(
                timestamp=time.time(),
                system=system_metrics,
                python=PythonInfo(
                    version=str(python_info["version"]),
                    platform=str(python_info["platform"]),
                    gc_counts=tuple(python_info["gc_counts"]),  # type: ignore[arg-type]
                ),
                application=application_metrics,
            )

        except Exception as e:
            self.logger.error(f"Metrics endpoint failed: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Metrics collection failed: {str(e)}"
            ) from e

    async def info(self, request: Request) -> InfoResponse:
        """
        Endpoint de información de la aplicación.

        Parameters
        ----------
        request : Request
            Request de FastAPI.

        Returns
        -------
        InfoResponse
            Información de la aplicación.

        Examples
        --------
        GET /diagnostics/info
        """
        try:
            health_checker = self.health_checker or get_health_checker()

            from .models import ApplicationInfo
            from .models import DependenciesInfo
            from .models import EnvironmentInfo

            return InfoResponse(
                timestamp=time.time(),
                application=ApplicationInfo(
                    name="TurboAPI",
                    version=health_checker.version,
                    uptime_seconds=time.time() - health_checker.start_time,
                ),
                environment=EnvironmentInfo(
                    python_version=sys.version,
                    platform=platform.platform(),
                    architecture=platform.architecture(),
                    processor=platform.processor(),
                ),
                dependencies=DependenciesInfo(
                    fastapi=True,
                    pydantic=True,
                    structlog=True,
                ),
            )

        except Exception as e:
            self.logger.error(f"Info endpoint failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Info collection failed: {str(e)}") from e

    async def system(self, request: Request) -> SystemResponse:
        """
        Endpoint de información del sistema.

        Parameters
        ----------
        request : Request
            Request de FastAPI.

        Returns
        -------
        SystemResponse
            Información del sistema.

        Examples
        --------
        GET /diagnostics/system
        """
        try:
            # Obtener métricas desde OpenTelemetry
            system_metrics_data = get_system_metrics()

            # Construir información del sistema
            system_info = {
                "hostname": platform.node(),
                "platform": platform.platform(),
                "architecture": platform.architecture(),
                "processor": platform.processor(),
                "python_version": sys.version,
            }

            cpu_info = {
                "count": 1,  # Fallback, se puede mejorar
                "percent": system_metrics_data["cpu_percent"],
                "freq": None,
            }

            memory_info = {
                "total": system_metrics_data["memory_total"],
                "available": system_metrics_data["memory_available"],
                "percent": system_metrics_data["memory_percent"],
                "used": (
                    system_metrics_data["memory_total"] - system_metrics_data["memory_available"]
                ),
            }

            disk_info = {
                "total": system_metrics_data["disk_total"],
                "used": system_metrics_data["disk_used"],
                "free": system_metrics_data["disk_free"],
                "percent": system_metrics_data["disk_percent"],
            }

            from .models import CPUInfo
            from .models import DiskInfo
            from .models import MemoryInfo
            from .models import SystemInfo

            return SystemResponse(
                timestamp=time.time(),
                system=SystemInfo(
                    hostname=str(system_info["hostname"]),
                    platform=str(system_info["platform"]),
                    architecture=system_info["architecture"],  # type: ignore[arg-type]
                    processor=str(system_info["processor"]),
                    python_version=str(system_info["python_version"]),
                ),
                cpu=CPUInfo(**cpu_info),
                memory=MemoryInfo(**memory_info),
                disk=DiskInfo(**disk_info),
            )

        except Exception as e:
            self.logger.error(f"System endpoint failed: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"System info collection failed: {str(e)}"
            ) from e

    async def memory(self, request: Request) -> MemoryResponse:
        """
        Endpoint de información de memoria.

        Parameters
        ----------
        request : Request
            Request de FastAPI.

        Returns
        -------
        MemoryResponse
            Información de memoria.

        Examples
        --------
        GET /diagnostics/memory
        """
        try:
            # Obtener métricas desde OpenTelemetry
            system_metrics_data = get_system_metrics()
            process_metrics_data = get_process_metrics()

            # Construir información del proceso
            process_info = {
                "pid": process_metrics_data["pid"],
                "memory": {
                    "rss": process_metrics_data["memory_rss"],
                    "vms": process_metrics_data["memory_vms"],
                    "percent": process_metrics_data["memory_percent"],
                },
                "num_threads": process_metrics_data["num_threads"],
            }

            system_memory = {
                "total": system_metrics_data["memory_total"],
                "available": system_metrics_data["memory_available"],
                "percent": system_metrics_data["memory_percent"],
                "used": (
                    system_metrics_data["memory_total"] - system_metrics_data["memory_available"]
                ),
            }

            from .models import MemoryInfo
            from .models import ProcessInfo
            from .models import PythonInfo

            return MemoryResponse(
                timestamp=time.time(),
                process=ProcessInfo(**process_info),
                system=MemoryInfo(**system_memory),
                python=PythonInfo(
                    version=sys.version,
                    platform=platform.platform(),
                    gc_counts=gc.get_count(),
                    gc_threshold=gc.get_threshold(),
                ),
            )

        except Exception as e:
            self.logger.error(f"Memory endpoint failed: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Memory info collection failed: {str(e)}"
            ) from e

    async def garbage_collection(self, request: Request) -> GarbageCollectionResponse:
        """
        Endpoint para forzar garbage collection.

        Parameters
        ----------
        request : Request
            Request de FastAPI.

        Returns
        -------
        GarbageCollectionResponse
            Resultado del garbage collection.

        Examples
        --------
        POST /diagnostics/gc
        """
        try:
            # Obtener estadísticas antes del GC
            before_counts = gc.get_count()
            process_metrics = get_process_metrics()
            before_memory = {
                "rss": process_metrics["memory_rss"],
                "vms": process_metrics["memory_vms"],
                "percent": process_metrics["memory_percent"],
            }

            # Forzar garbage collection
            collected = gc.collect()

            # Obtener estadísticas después del GC
            after_counts = gc.get_count()
            process_metrics_after = get_process_metrics()
            after_memory = {
                "rss": process_metrics_after["memory_rss"],
                "vms": process_metrics_after["memory_vms"],
                "percent": process_metrics_after["memory_percent"],
            }

            from .models import GarbageCollectionInfo

            return GarbageCollectionResponse(
                timestamp=time.time(),
                garbage_collection=GarbageCollectionInfo(
                    collected_objects=collected,
                    before={
                        "gc_counts": before_counts,
                        "memory_rss": before_memory["rss"],
                        "memory_vms": before_memory["vms"],
                    },
                    after={
                        "gc_counts": after_counts,
                        "memory_rss": after_memory["rss"],
                        "memory_vms": after_memory["vms"],
                    },
                    memory_freed=before_memory["rss"] - after_memory["rss"],
                ),
            )

        except Exception as e:
            self.logger.error(f"Garbage collection endpoint failed: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Garbage collection failed: {str(e)}"
            ) from e

    async def tracing_info(self, request: Request) -> TracingResponse:
        """
        Endpoint de información de tracing.

        Parameters
        ----------
        request : Request
            Request de FastAPI.

        Returns
        -------
        TracingResponse
            Información de tracing.

        Examples
        --------
        GET /diagnostics/tracing
        """
        try:
            tracing_data = {
                "timestamp": time.time(),
                "tracing": {
                    "enabled": False,
                    "provider": None,
                    "service_name": None,
                },
            }

            # Intentar obtener información del tracer
            try:
                tracer = get_tracer()
                tracing_data["tracing"] = {
                    "enabled": True,
                    "provider": "OpenTelemetry",
                    "service_name": tracer.config.service_name,
                    "jaeger_enabled": tracer.config.enable_jaeger,
                    "otlp_enabled": tracer.config.enable_otlp,
                    "auto_instrumentation": tracer.config.enable_auto_instrumentation,
                }
            except RuntimeError:
                # Tracing no configurado
                pass

            from .models import TracingInfo

            return TracingResponse(
                timestamp=time.time(),
                tracing=TracingInfo(**tracing_data["tracing"]),  # type: ignore[arg-type]
            )

        except Exception as e:
            self.logger.error(f"Tracing info endpoint failed: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Tracing info collection failed: {str(e)}"
            ) from e


def create_diagnostics_router(health_checker: HealthChecker | None = None) -> APIRouter:
    """
    Crea un router de diagnóstico para FastAPI.

    Parameters
    ----------
    health_checker : Optional[HealthChecker], optional
        Health checker a usar (default: None, usa el global).

    Returns
    -------
    APIRouter
        Router de FastAPI con endpoints de diagnóstico.

    Examples
    --------
    >>> router = create_diagnostics_router()
    >>> app.include_router(router, prefix="/diagnostics")
    """
    diagnostics_router = DiagnosticsRouter(health_checker)
    return diagnostics_router.router
