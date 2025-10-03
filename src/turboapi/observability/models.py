"""Modelos de datos para el sistema de observabilidad.

Este módulo contiene todos los modelos Pydantic utilizados por los endpoints
de diagnóstico y observabilidad de TurboAPI. Estos modelos se utilizan para
generar automáticamente la documentación OpenAPI y validar las respuestas.
"""

from typing import Any

from pydantic import BaseModel
from pydantic import Field


class SystemInfo(BaseModel):
    """Información básica del sistema operativo.

    Contiene información fundamental sobre el sistema donde se ejecuta la aplicación,
    incluyendo detalles del hardware y software base.

    Examples
    --------
    >>> system_info = SystemInfo(
    ...     hostname="server-01",
    ...     platform="Windows-10-10.0.19041-SP0",
    ...     architecture=("64bit", "WindowsPE"),
    ...     processor="Intel64 Family 6 Model 142 Stepping 10, GenuineIntel",
    ...     python_version="3.12.7"
    ... )
    """

    hostname: str = Field(description="Nombre del host del sistema", examples=["server-01"])
    platform: str = Field(
        description="Plataforma del sistema operativo", examples=["Windows-10-10.0.19041-SP0"]
    )
    architecture: tuple[str, str] = Field(
        description="Arquitectura del sistema (bits, tipo)", examples=[("64bit", "WindowsPE")]
    )
    processor: str = Field(
        description="Información del procesador",
        examples=["Intel64 Family 6 Model 142 Stepping 10, GenuineIntel"],
    )
    python_version: str = Field(
        description="Versión de Python en ejecución",
        examples=[
            "3.12.7 (tags/v3.12.7:ccb0e6a, Dec 19 2023, 19:13:39) [MSC v.1937 64 bit (AMD64)]"
        ],
    )


class CPUInfo(BaseModel):
    """Información del procesador (CPU).

    Contiene métricas y detalles sobre el uso y características del procesador.

    Examples
    --------
    >>> cpu_info = CPUInfo(
    ...     count=8,
    ...     percent=25.5,
    ...     freq={"current": 2400.0, "min": 800.0, "max": 3200.0}
    ... )
    """

    count: int = Field(description="Número de núcleos de CPU disponibles", examples=[8], ge=1)
    percent: float = Field(
        description="Porcentaje de uso actual de CPU", examples=[25.5], ge=0.0, le=100.0
    )
    freq: dict[str, Any] | None = Field(
        default=None,
        description="Información de frecuencia del CPU (si está disponible)",
        examples=[{"current": 2400.0, "min": 800.0, "max": 3200.0}],
    )


class MemoryInfo(BaseModel):
    """Información de memoria del sistema.

    Contiene métricas sobre el uso de memoria RAM del sistema.

    Examples
    --------
    >>> memory_info = MemoryInfo(
    ...     total=17179869184,  # 16 GB
    ...     available=8589934592,  # 8 GB
    ...     percent=50.0,
    ...     used=8589934592  # 8 GB
    ... )
    """

    total: int = Field(
        description="Memoria total del sistema en bytes", examples=[17179869184], ge=0
    )
    available: int = Field(description="Memoria disponible en bytes", examples=[8589934592], ge=0)
    percent: float = Field(
        description="Porcentaje de memoria utilizada", examples=[50.0], ge=0.0, le=100.0
    )
    used: int = Field(description="Memoria utilizada en bytes", examples=[8589934592], ge=0)


class DiskInfo(BaseModel):
    """Información de almacenamiento en disco.

    Contiene métricas sobre el uso de espacio en disco del sistema.

    Examples
    --------
    >>> disk_info = DiskInfo(
    ...     total=1000000000000,  # 1 TB
    ...     used=500000000000,    # 500 GB
    ...     free=500000000000,    # 500 GB
    ...     percent=50.0
    ... )
    """

    total: int = Field(
        description="Espacio total en disco en bytes", examples=[1000000000000], ge=0
    )
    used: int = Field(
        description="Espacio utilizado en disco en bytes", examples=[500000000000], ge=0
    )
    free: int = Field(description="Espacio libre en disco en bytes", examples=[500000000000], ge=0)
    percent: float = Field(
        description="Porcentaje de espacio utilizado", examples=[50.0], ge=0.0, le=100.0
    )


class ProcessMemoryInfo(BaseModel):
    """Información de memoria del proceso actual.

    Contiene métricas sobre el uso de memoria del proceso de la aplicación.

    Examples
    --------
    >>> process_memory = ProcessMemoryInfo(
    ...     rss=52428800,    # 50 MB
    ...     vms=104857600,   # 100 MB
    ...     percent=0.3
    ... )
    """

    rss: int = Field(
        description="Memoria física utilizada (Resident Set Size) en bytes",
        examples=[52428800],
        ge=0,
    )
    vms: int = Field(
        description="Memoria virtual utilizada (Virtual Memory Size) en bytes",
        examples=[104857600],
        ge=0,
    )
    percent: float = Field(
        description="Porcentaje de memoria del sistema utilizada por el proceso",
        examples=[0.3],
        ge=0.0,
    )


class ProcessInfo(BaseModel):
    """Información del proceso actual de la aplicación.

    Contiene detalles sobre el proceso donde se ejecuta la aplicación.

    Examples
    --------
    >>> process_info = ProcessInfo(
    ...     pid=1234,
    ...     memory=ProcessMemoryInfo(rss=52428800, vms=104857600, percent=0.3),
    ...     num_threads=8
    ... )
    """

    pid: int = Field(description="ID del proceso (Process ID)", examples=[1234], ge=1)
    memory: ProcessMemoryInfo = Field(description="Información de memoria del proceso")
    num_threads: int = Field(description="Número de hilos del proceso", examples=[8], ge=1)


class PythonInfo(BaseModel):
    """Información del entorno Python.

    Contiene detalles sobre la versión de Python y el recolector de basura.

    Examples
    --------
    >>> python_info = PythonInfo(
    ...     version="3.12.7",
    ...     platform="Windows-10-10.0.19041-SP0",
    ...     gc_counts=(177, 1, 3),
    ...     gc_threshold=(700, 10, 10)
    ... )
    """

    version: str = Field(
        description="Versión completa de Python",
        examples=[
            "3.12.7 (tags/v3.12.7:ccb0e6a, Dec 19 2023, 19:13:39) [MSC v.1937 64 bit (AMD64)]"
        ],
    )
    platform: str = Field(
        description="Plataforma de Python", examples=["Windows-10-10.0.19041-SP0"]
    )
    gc_counts: tuple[int, int, int] = Field(
        description="Contadores del recolector de basura (gen0, gen1, gen2)",
        examples=[(177, 1, 3)],
    )
    gc_threshold: tuple[int, int, int] | None = Field(
        default=None,
        description="Umbrales del recolector de basura (gen0, gen1, gen2)",
        examples=[(700, 10, 10)],
    )


class ApplicationInfo(BaseModel):
    """Información de la aplicación TurboAPI.

    Contiene detalles sobre la aplicación, incluyendo nombre, versión y tiempo de actividad.

    Examples
    --------
    >>> app_info = ApplicationInfo(
    ...     name="TurboAPI",
    ...     version="1.0.0",
    ...     uptime_seconds=3600.5
    ... )
    """

    name: str = Field(description="Nombre de la aplicación", examples=["TurboAPI"])
    version: str = Field(description="Versión de la aplicación", examples=["1.0.0"])
    uptime_seconds: float = Field(
        description="Tiempo de actividad en segundos", examples=[3600.5], ge=0.0
    )


class EnvironmentInfo(BaseModel):
    """Información del entorno de ejecución.

    Contiene detalles sobre el entorno donde se ejecuta la aplicación.

    Examples
    --------
    >>> env_info = EnvironmentInfo(
    ...     python_version="3.12.7",
    ...     platform="Windows-10-10.0.19041-SP0",
    ...     architecture=("64bit", "WindowsPE"),
    ...     processor="Intel64 Family 6 Model 142 Stepping 10, GenuineIntel"
    ... )
    """

    python_version: str = Field(
        description="Versión de Python",
        examples=[
            "3.12.7 (tags/v3.12.7:ccb0e6a, Dec 19 2023, 19:13:39) [MSC v.1937 64 bit (AMD64)]"
        ],
    )
    platform: str = Field(
        description="Plataforma del sistema", examples=["Windows-10-10.0.19041-SP0"]
    )
    architecture: tuple[str, str] = Field(
        description="Arquitectura del sistema", examples=[("64bit", "WindowsPE")]
    )
    processor: str = Field(
        description="Información del procesador",
        examples=["Intel64 Family 6 Model 142 Stepping 10, GenuineIntel"],
    )


class DependenciesInfo(BaseModel):
    """Información de dependencias principales.

    Indica qué dependencias principales están disponibles en el entorno.

    Examples
    --------
    >>> deps_info = DependenciesInfo(
    ...     fastapi=True,
    ...     pydantic=True,
    ...     structlog=True
    ... )
    """

    fastapi: bool = Field(description="FastAPI está disponible", examples=[True])
    pydantic: bool = Field(description="Pydantic está disponible", examples=[True])
    structlog: bool = Field(description="Structlog está disponible", examples=[True])


class TracingInfo(BaseModel):
    """Información de tracing y observabilidad distribuida.

    Contiene detalles sobre la configuración de tracing de la aplicación.

    Examples
    --------
    >>> tracing_info = TracingInfo(
    ...     enabled=True,
    ...     provider="OpenTelemetry",
    ...     service_name="turboapi-service",
    ...     jaeger_enabled=True,
    ...     otlp_enabled=False,
    ...     auto_instrumentation=True
    ... )
    """

    enabled: bool = Field(description="Tracing está habilitado", examples=[True])
    provider: str | None = Field(
        default=None, description="Proveedor de tracing", examples=["OpenTelemetry"]
    )
    service_name: str | None = Field(
        default=None, description="Nombre del servicio para tracing", examples=["turboapi-service"]
    )
    jaeger_enabled: bool | None = Field(
        default=None, description="Jaeger está habilitado", examples=[True]
    )
    otlp_enabled: bool | None = Field(
        default=None, description="OTLP está habilitado", examples=[False]
    )
    auto_instrumentation: bool | None = Field(
        default=None, description="Instrumentación automática está habilitada", examples=[True]
    )


class GarbageCollectionInfo(BaseModel):
    """Información de recolección de basura (Garbage Collection).

    Contiene estadísticas sobre la recolección de basura de Python.

    Examples
    --------
    >>> gc_info = GarbageCollectionInfo(
    ...     collected_objects=42,
    ...     before={"gc_counts": (177, 1, 3), "memory_rss": 52428800, "memory_vms": 104857600},
    ...     after={"gc_counts": (0, 0, 0), "memory_rss": 41943040, "memory_vms": 83886080},
    ...     memory_freed=10485760
    ... )
    """

    collected_objects: int = Field(
        description="Número de objetos recolectados", examples=[42], ge=0
    )
    before: dict[str, Any] = Field(
        description="Estado antes del garbage collection",
        examples=[{"gc_counts": (177, 1, 3), "memory_rss": 52428800, "memory_vms": 104857600}],
    )
    after: dict[str, Any] = Field(
        description="Estado después del garbage collection",
        examples=[{"gc_counts": (0, 0, 0), "memory_rss": 41943040, "memory_vms": 83886080}],
    )
    memory_freed: int = Field(description="Memoria liberada en bytes", examples=[10485760], ge=0)


# Respuestas de endpoints
class HealthResponse(BaseModel):
    """Respuesta del endpoint de health check.

    Contiene el estado de salud completo del sistema con todos los checks realizados.

    Examples
    --------
    >>> health_response = HealthResponse(
    ...     status="healthy",
    ...     timestamp=1704067200.0,
    ...     version="1.0.0",
    ...     uptime_seconds=3600.5,
    ...     checks=[{"name": "database", "status": "healthy", "message": "Connection OK"}],
    ...     summary={"healthy": 1, "degraded": 0, "unhealthy": 0, "unknown": 0}
    ... )
    """

    status: str = Field(
        description="Estado general del sistema",
        examples=["healthy"],
        pattern="^(healthy|degraded|unhealthy|unknown)$",
    )
    timestamp: float = Field(
        description="Timestamp Unix de la verificación", examples=[1704067200.0]
    )
    version: str = Field(description="Versión de la aplicación", examples=["1.0.0"])
    uptime_seconds: float = Field(
        description="Tiempo de actividad en segundos", examples=[3600.5], ge=0.0
    )
    checks: list[dict[str, Any]] = Field(
        description="Lista de checks individuales realizados",
        examples=[[{"name": "database", "status": "healthy", "message": "Connection OK"}]],
    )
    summary: dict[str, int] = Field(
        description="Resumen de estados de los checks",
        examples=[{"healthy": 1, "degraded": 0, "unhealthy": 0, "unknown": 0}],
    )


class ReadinessResponse(BaseModel):
    """Respuesta del endpoint de readiness probe.

    Indica si la aplicación está lista para recibir tráfico (Kubernetes readiness probe).

    Examples
    --------
    >>> readiness_response = ReadinessResponse(
    ...     ready=True,
    ...     status="healthy",
    ...     timestamp=1704067200.0
    ... )
    """

    ready: bool = Field(
        description="La aplicación está lista para recibir tráfico", examples=[True]
    )
    status: str = Field(
        description="Estado del sistema",
        examples=["healthy"],
        pattern="^(healthy|degraded|unhealthy|unknown)$",
    )
    timestamp: float = Field(
        description="Timestamp Unix de la verificación", examples=[1704067200.0]
    )


class LivenessResponse(BaseModel):
    """Respuesta del endpoint de liveness probe.

    Indica si la aplicación está viva y funcionando (Kubernetes liveness probe).

    Examples
    --------
    >>> liveness_response = LivenessResponse(
    ...     alive=True,
    ...     timestamp=1704067200.0,
    ...     uptime=3600.5
    ... )
    """

    alive: bool = Field(description="La aplicación está viva y funcionando", examples=[True])
    timestamp: float = Field(
        description="Timestamp Unix de la verificación", examples=[1704067200.0]
    )
    uptime: float = Field(
        description="Tiempo de actividad del proceso en segundos", examples=[3600.5], ge=0.0
    )


class MetricsResponse(BaseModel):
    """Respuesta del endpoint de métricas de la aplicación.

    Contiene métricas del sistema, Python y la aplicación.

    Examples
    --------
    >>> metrics_response = MetricsResponse(
    ...     timestamp=1704067200.0,
    ...     system={
    ...         "cpu_percent": 25.5,
    ...         "memory": {"rss": 52428800, "vms": 104857600},
    ...         "num_threads": 8
    ...     },
    ...     python=PythonInfo(version="3.12.7", platform="Windows-10", gc_counts=(177, 1, 3)),
    ...     application={"metrics_collector_initialized": True}
    ... )
    """

    timestamp: float = Field(description="Timestamp Unix de las métricas", examples=[1704067200.0])
    system: dict[str, Any] = Field(
        description="Métricas del sistema",
        examples=[
            {
                "cpu_percent": 25.5,
                "memory": {"rss": 52428800, "vms": 104857600},
                "num_threads": 8,
            }
        ],
    )
    python: PythonInfo = Field(description="Información de Python")
    application: dict[str, Any] = Field(
        description="Métricas de la aplicación",
        examples=[{"metrics_collector_initialized": True}],
    )


class InfoResponse(BaseModel):
    """Respuesta del endpoint de información de la aplicación.

    Contiene información general sobre la aplicación, entorno y dependencias.

    Examples
    --------
    >>> info_response = InfoResponse(
    ...     timestamp=1704067200.0,
    ...     application=ApplicationInfo(name="TurboAPI", version="1.0.0", uptime_seconds=3600.5),
    ...     environment=EnvironmentInfo(
    ...         python_version="3.12.7",
    ...         platform="Windows-10",
    ...         architecture=("64bit", "WindowsPE"),
    ...         processor="Intel64"
    ...     ),
    ...     dependencies=DependenciesInfo(fastapi=True, pydantic=True, structlog=True)
    ... )
    """

    timestamp: float = Field(
        description="Timestamp Unix de la información", examples=[1704067200.0]
    )
    application: ApplicationInfo = Field(description="Información de la aplicación")
    environment: EnvironmentInfo = Field(description="Información del entorno")
    dependencies: DependenciesInfo = Field(description="Información de dependencias")


class SystemResponse(BaseModel):
    """Respuesta del endpoint de información del sistema.

    Contiene información detallada sobre el sistema operativo, CPU, memoria y disco.

    Examples
    --------
    >>> system_response = SystemResponse(
    ...     timestamp=1704067200.0,
    ...     system=SystemInfo(
    ...         hostname="server-01",
    ...         platform="Windows-10",
    ...         architecture=("64bit", "WindowsPE"),
    ...         processor="Intel64",
    ...         python_version="3.12.7"
    ...     ),
    ...     cpu=CPUInfo(
    ...         count=8,
    ...         percent=25.5,
    ...         freq={"current": 2400.0, "min": 800.0, "max": 3200.0}
    ...     ),
    ...     memory=MemoryInfo(
    ...         total=17179869184,
    ...         available=8589934592,
    ...         percent=50.0,
    ...         used=8589934592
    ...     ),
    ...     disk=DiskInfo(total=1000000000000, used=500000000000, free=500000000000, percent=50.0)
    ... )
    """

    timestamp: float = Field(
        description="Timestamp Unix de la información del sistema", examples=[1704067200.0]
    )
    system: SystemInfo = Field(description="Información básica del sistema")
    cpu: CPUInfo = Field(description="Información del procesador")
    memory: MemoryInfo = Field(description="Información de memoria")
    disk: DiskInfo = Field(description="Información de disco")


class MemoryResponse(BaseModel):
    """Respuesta del endpoint de información de memoria.

    Contiene información detallada sobre el uso de memoria del proceso y del sistema.

    Examples
    --------
    >>> memory_response = MemoryResponse(
    ...     timestamp=1704067200.0,
    ...     process=ProcessInfo(
    ...         pid=1234,
    ...         memory=ProcessMemoryInfo(rss=52428800, vms=104857600, percent=0.3),
    ...         num_threads=8
    ...     ),
    ...     system=MemoryInfo(
    ...         total=17179869184,
    ...         available=8589934592,
    ...         percent=50.0,
    ...         used=8589934592
    ...     ),
    ...     python=PythonInfo(
    ...         version="3.12.7",
    ...         platform="Windows-10",
    ...         gc_counts=(177, 1, 3),
    ...         gc_threshold=(700, 10, 10)
    ...     )
    ... )
    """

    timestamp: float = Field(
        description="Timestamp Unix de la información de memoria", examples=[1704067200.0]
    )
    process: ProcessInfo = Field(description="Información del proceso")
    system: MemoryInfo = Field(description="Información de memoria del sistema")
    python: PythonInfo = Field(description="Información de Python")


class GarbageCollectionResponse(BaseModel):
    """Respuesta del endpoint de garbage collection.

    Contiene estadísticas sobre la recolección de basura forzada.

    Examples
    --------
    >>> gc_response = GarbageCollectionResponse(
    ...     timestamp=1704067200.0,
    ...     garbage_collection=GarbageCollectionInfo(
    ...         collected_objects=42,
    ...         before={"gc_counts": (177, 1, 3), "memory_rss": 52428800, "memory_vms": 104857600},
    ...         after={"gc_counts": (0, 0, 0), "memory_rss": 41943040, "memory_vms": 83886080},
    ...         memory_freed=10485760
    ...     )
    ... )
    """

    timestamp: float = Field(
        description="Timestamp Unix de la recolección de basura", examples=[1704067200.0]
    )
    garbage_collection: GarbageCollectionInfo = Field(
        description="Estadísticas de garbage collection"
    )


class TracingResponse(BaseModel):
    """Respuesta del endpoint de información de tracing.

    Contiene información sobre la configuración de tracing de la aplicación.

    Examples
    --------
    >>> tracing_response = TracingResponse(
    ...     timestamp=1704067200.0,
    ...     tracing=TracingInfo(
    ...         enabled=True,
    ...         provider="OpenTelemetry",
    ...         service_name="turboapi-service",
    ...         jaeger_enabled=True,
    ...         otlp_enabled=False,
    ...         auto_instrumentation=True
    ...     )
    ... )
    """

    timestamp: float = Field(
        description="Timestamp Unix de la información de tracing", examples=[1704067200.0]
    )
    tracing: TracingInfo = Field(description="Información de tracing")


class ErrorResponse(BaseModel):
    """Respuesta de error estándar.

    Modelo para respuestas de error en los endpoints de diagnóstico.

    Examples
    --------
    >>> error_response = ErrorResponse(
    ...     error="Service unavailable",
    ...     timestamp=1704067200.0,
    ...     detail="Database connection failed"
    ... )
    """

    error: str = Field(description="Mensaje de error principal", examples=["Service unavailable"])
    timestamp: float = Field(description="Timestamp Unix del error", examples=[1704067200.0])
    detail: str | None = Field(
        default=None,
        description="Detalle adicional del error",
        examples=["Database connection failed"],
    )
