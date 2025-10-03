"""Observability module for TurboAPI."""

from .apm import APMConfig
from .apm import APMManager
from .apm import BaseAPMProvider
from .apm import OpenTelemetryAPMProvider
from .apm import apm_async_transaction
from .apm import apm_transaction
from .apm import configure_apm
from .apm import get_apm_manager
from .diagnostics import DiagnosticsRouter
from .diagnostics import create_diagnostics_router
from .health import BaseHealthCheck
from .health import DatabaseHealthCheck
from .health import ExternalServiceHealthCheck
from .health import HealthChecker
from .health import HealthCheckResult
from .health import HealthStatus
from .health import RedisHealthCheck
from .health import configure_health_checks
from .health import get_health_checker
from .logging import LoggingConfig
from .logging import LogLevel
from .logging import StructuredLogger
from .logging import TurboLogging
from .logging import configure_logging
from .logging import get_logger
from .metrics import MetricConfig
from .metrics import OpenTelemetryCollector
from .metrics import configure_metrics
from .metrics import create_counter
from .metrics import create_gauge
from .metrics import create_histogram
from .metrics import create_summary
from .metrics import get_metrics_collector
from .starter import ObservabilityStarter
from .tracing import OpenTelemetryTracer
from .tracing import TracingConfig
from .tracing import add_event
from .tracing import configure_tracing
from .tracing import get_tracer
from .tracing import set_attribute
from .tracing import start_as_current_span
from .tracing import start_span

__all__ = [
    # Logging
    "LogLevel",
    "LoggingConfig",
    "StructuredLogger",
    "TurboLogging",
    "configure_logging",
    "get_logger",
    # Metrics
    "MetricConfig",
    "OpenTelemetryCollector",
    "configure_metrics",
    "create_counter",
    "create_gauge",
    "create_histogram",
    "create_summary",
    "get_metrics_collector",
    # Tracing
    "TracingConfig",
    "OpenTelemetryTracer",
    "configure_tracing",
    "get_tracer",
    "start_span",
    "start_as_current_span",
    "add_event",
    "set_attribute",
    # Health Checks
    "HealthStatus",
    "HealthCheckResult",
    "BaseHealthCheck",
    "DatabaseHealthCheck",
    "RedisHealthCheck",
    "ExternalServiceHealthCheck",
    "HealthChecker",
    "configure_health_checks",
    "get_health_checker",
    # Diagnostics
    "DiagnosticsRouter",
    "create_diagnostics_router",
    # APM
    "APMConfig",
    "APMManager",
    "BaseAPMProvider",
    "OpenTelemetryAPMProvider",
    "apm_transaction",
    "apm_async_transaction",
    "configure_apm",
    "get_apm_manager",
    # Starter
    "ObservabilityStarter",
]
