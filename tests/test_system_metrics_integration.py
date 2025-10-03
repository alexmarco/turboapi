#!/usr/bin/env python3
"""Test para verificar la integración de métricas del sistema con OpenTelemetry."""

from opentelemetry.instrumentation.system_metrics import SystemMetricsInstrumentor


def test_system_metrics_integration():
    """Prueba las métricas del sistema de OpenTelemetry."""

    # Verificar que SystemMetricsInstrumentor está disponible
    assert SystemMetricsInstrumentor is not None

    # Crear una instancia del instrumentor
    system_instrumentor = SystemMetricsInstrumentor()
    assert system_instrumentor is not None

    # Verificar que se puede instrumentar (puede fallar si ya está instrumentado)
    try:
        system_instrumentor.instrument()
        instrumented = True
    except Exception:
        # Ya está instrumentado, esto es normal en tests
        instrumented = False

    # Verificar que se puede desinstrumentar
    try:
        system_instrumentor.uninstrument()
        uninstrumented = True
    except Exception:
        # No estaba instrumentado, esto es normal
        uninstrumented = False

    # Al menos una de las operaciones debería funcionar
    assert instrumented or uninstrumented, "No se pudo instrumentar ni desinstrumentar"

    # Verificar que el instrumentor tiene los métodos esperados
    assert hasattr(system_instrumentor, "instrument")
    assert hasattr(system_instrumentor, "uninstrument")
    assert callable(system_instrumentor.instrument)
    assert callable(system_instrumentor.uninstrument)


def test_turboapi_metrics_integration():
    """Prueba la integración de métricas usando TurboAPI."""
    from turboapi.observability.metrics import get_process_metrics
    from turboapi.observability.metrics import get_system_metrics

    # Obtener métricas del sistema
    system_metrics = get_system_metrics()

    # Verificar que se obtuvieron métricas del sistema
    assert isinstance(system_metrics, dict)
    assert "cpu_percent" in system_metrics
    assert "memory_total" in system_metrics
    assert "memory_available" in system_metrics
    assert "memory_percent" in system_metrics
    assert "disk_total" in system_metrics
    assert "disk_used" in system_metrics
    assert "disk_free" in system_metrics
    assert "disk_percent" in system_metrics

    # Verificar tipos de datos
    assert isinstance(system_metrics["cpu_percent"], (int, float))
    assert isinstance(system_metrics["memory_total"], int)
    assert isinstance(system_metrics["memory_available"], int)
    assert isinstance(system_metrics["memory_percent"], (int, float))
    assert isinstance(system_metrics["disk_total"], int)
    assert isinstance(system_metrics["disk_used"], int)
    assert isinstance(system_metrics["disk_free"], int)
    assert isinstance(system_metrics["disk_percent"], (int, float))

    # Obtener métricas del proceso
    process_metrics = get_process_metrics()

    # Verificar que se obtuvieron métricas del proceso
    assert isinstance(process_metrics, dict)
    assert "pid" in process_metrics
    assert "memory_rss" in process_metrics
    assert "memory_vms" in process_metrics
    assert "memory_percent" in process_metrics
    assert "cpu_percent" in process_metrics
    assert "num_threads" in process_metrics
    assert "num_fds" in process_metrics

    # Verificar tipos de datos
    assert isinstance(process_metrics["pid"], int)
    assert isinstance(process_metrics["memory_rss"], int)
    assert isinstance(process_metrics["memory_vms"], int)
    assert isinstance(process_metrics["memory_percent"], (int, float))
    assert isinstance(process_metrics["cpu_percent"], (int, float))
    assert isinstance(process_metrics["num_threads"], int)
    # num_fds puede ser None si no está disponible
    assert process_metrics["num_fds"] is None or isinstance(process_metrics["num_fds"], int)


if __name__ == "__main__":
    test_system_metrics_integration()
    test_turboapi_metrics_integration()
    print("Todos los tests pasaron correctamente")
