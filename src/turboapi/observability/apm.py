"""
Sistema de APM (Application Performance Monitoring) para TurboAPI.

Este módulo proporciona integración con herramientas APM populares como New Relic,
DataDog, y Elastic APM, permitiendo monitoreo avanzado de rendimiento de aplicaciones.
"""

import contextlib
from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


@dataclass
class APMConfig:
    """
    Configuración para el sistema APM.

    Parameters
    ----------
    enabled : bool, optional
        Si el sistema APM está habilitado (default: True).
    service_name : str, optional
        Nombre del servicio para APM (default: "turboapi-app").
    environment : str, optional
        Entorno de la aplicación (default: "development").
    version : str, optional
        Versión de la aplicación (default: "1.0.0").
    sample_rate : float, optional
        Tasa de muestreo para traces (default: 1.0).
    max_attributes : int, optional
        Número máximo de atributos por span (default: 128).
    max_events : int, optional
        Número máximo de eventos por span (default: 128).
    max_links : int, optional
        Número máximo de links por span (default: 128).
    exporters : List[str], optional
        Lista de exporters a usar (default: ["otlp"]).

    Examples
    --------
    >>> config = APMConfig(
    ...     service_name="my-api",
    ...     environment="production",
    ...     version="2.1.0",
    ...     sample_rate=0.1
    ... )
    """

    enabled: bool = True
    service_name: str = "turboapi-app"
    environment: str = "development"
    version: str = "1.0.0"
    sample_rate: float = 1.0
    max_attributes: int = 128
    max_events: int = 128
    max_links: int = 128
    exporters: list[str] = field(default_factory=lambda: ["otlp"])

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "APMConfig":
        """
        Crea una configuración APM desde un diccionario.

        Parameters
        ----------
        data : Dict[str, Any]
            Diccionario con la configuración.

        Returns
        -------
        APMConfig
            Configuración APM creada.

        Examples
        --------
        >>> config_data = {
        ...     "enabled": True,
        ...     "service_name": "my-api",
        ...     "environment": "production"
        ... }
        >>> config = APMConfig.from_dict(config_data)
        """
        return cls(**data)


class BaseAPMProvider(ABC):
    """Proveedor base para herramientas APM."""

    def __init__(self, config: APMConfig):
        """
        Inicializa el proveedor APM.

        Parameters
        ----------
        config : APMConfig
            Configuración del sistema APM.
        """
        self.config = config
        self._initialized = False

    @abstractmethod
    def initialize(self) -> None:
        """
        Inicializa el proveedor APM.

        Examples
        --------
        >>> provider = NewRelicAPMProvider(config)
        >>> provider.initialize()
        """
        pass

    @abstractmethod
    def start_transaction(self, name: str, transaction_type: str = "web") -> Any:
        """
        Inicia una transacción APM.

        Parameters
        ----------
        name : str
            Nombre de la transacción.
        transaction_type : str, optional
            Tipo de transacción (default: "web").

        Returns
        -------
        Any
            Objeto de transacción APM.

        Examples
        --------
        >>> transaction = provider.start_transaction("/api/users", "web")
        """
        pass

    @abstractmethod
    def end_transaction(self, transaction: Any, status: str = "success") -> None:
        """
        Finaliza una transacción APM.

        Parameters
        ----------
        transaction : Any
            Objeto de transacción APM.
        status : str, optional
            Estado de la transacción (default: "success").

        Examples
        --------
        >>> provider.end_transaction(transaction, "success")
        """
        pass

    @abstractmethod
    def add_custom_attribute(self, transaction: Any, key: str, value: Any) -> None:
        """
        Añade un atributo personalizado a la transacción.

        Parameters
        ----------
        transaction : Any
            Objeto de transacción APM.
        key : str
            Clave del atributo.
        value : Any
            Valor del atributo.

        Examples
        --------
        >>> provider.add_custom_attribute(transaction, "user_id", "12345")
        """
        pass

    @abstractmethod
    def record_error(self, transaction: Any, error: Exception) -> None:
        """
        Registra un error en la transacción.

        Parameters
        ----------
        transaction : Any
            Objeto de transacción APM.
        error : Exception
            Error a registrar.

        Examples
        --------
        >>> provider.record_error(transaction, ValueError("Invalid input"))
        """
        pass

    @abstractmethod
    def record_metric(self, name: str, value: float, tags: dict[str, str] | None = None) -> None:
        """
        Registra una métrica personalizada.

        Parameters
        ----------
        name : str
            Nombre de la métrica.
        value : float
            Valor de la métrica.
        tags : Optional[Dict[str, str]], optional
            Tags para la métrica (default: None).

        Examples
        --------
        >>> provider.record_metric("response_time", 150.5, {"endpoint": "/api/users"})
        """
        pass


class OpenTelemetryAPMProvider(BaseAPMProvider):
    """Proveedor APM basado en OpenTelemetry."""

    def __init__(self, config: APMConfig):
        """
        Inicializa el proveedor OpenTelemetry APM.

        Parameters
        ----------
        config : APMConfig
            Configuración del sistema APM.
        """
        super().__init__(config)
        self._tracer_provider: TracerProvider | None = None
        self._tracer: Any = None

    def initialize(self) -> None:
        """
        Inicializa el proveedor OpenTelemetry APM.

        Examples
        --------
        >>> provider = OpenTelemetryAPMProvider(config)
        >>> provider.initialize()
        """
        if self._initialized:
            return

        # Configurar TracerProvider
        self._tracer_provider = TracerProvider(
            resource=None,  # Se configurará automáticamente
        )

        # Configurar exporters
        for exporter_name in self.config.exporters:
            if exporter_name == "otlp":
                self._setup_otlp_exporter()

        # Establecer el tracer provider global
        trace.set_tracer_provider(self._tracer_provider)

        # Obtener tracer
        self._tracer = trace.get_tracer(
            self.config.service_name,
            self.config.version,
        )

        self._initialized = True

    def _setup_otlp_exporter(self) -> None:
        """Configura el exporter OTLP."""
        try:
            exporter = OTLPSpanExporter(
                endpoint="http://localhost:4317",  # OTLP gRPC endpoint por defecto
                insecure=True,
            )

            span_processor = BatchSpanProcessor(exporter)
            if self._tracer_provider:
                self._tracer_provider.add_span_processor(span_processor)
        except Exception:
            # En caso de error, continuar sin el exporter
            pass

    def start_transaction(self, name: str, transaction_type: str = "web") -> Any:
        """
        Inicia una transacción APM usando OpenTelemetry.

        Parameters
        ----------
        name : str
            Nombre de la transacción.
        transaction_type : str, optional
            Tipo de transacción (default: "web").

        Returns
        -------
        Any
            Span de OpenTelemetry.

        Examples
        --------
        >>> span = provider.start_transaction("/api/users", "web")
        """
        if not self._initialized:
            self.initialize()

        if not self._tracer:
            return None

        span = self._tracer.start_span(
            name=name,
            attributes={
                "transaction.type": transaction_type,
                "service.name": self.config.service_name,
                "service.version": self.config.version,
                "service.environment": self.config.environment,
            },
        )

        return span

    def end_transaction(self, transaction: Any, status: str = "success") -> None:
        """
        Finaliza una transacción APM.

        Parameters
        ----------
        transaction : Any
            Span de OpenTelemetry.
        status : str, optional
            Estado de la transacción (default: "success").

        Examples
        --------
        >>> provider.end_transaction(span, "success")
        """
        if transaction:
            transaction.set_attribute("transaction.status", status)
            transaction.end()

    def add_custom_attribute(self, transaction: Any, key: str, value: Any) -> None:
        """
        Añade un atributo personalizado a la transacción.

        Parameters
        ----------
        transaction : Any
            Span de OpenTelemetry.
        key : str
            Clave del atributo.
        value : Any
            Valor del atributo.

        Examples
        --------
        >>> provider.add_custom_attribute(span, "user_id", "12345")
        """
        if transaction:
            transaction.set_attribute(key, value)

    def record_error(self, transaction: Any, error: Exception) -> None:
        """
        Registra un error en la transacción.

        Parameters
        ----------
        transaction : Any
            Span de OpenTelemetry.
        error : Exception
            Error a registrar.

        Examples
        --------
        >>> provider.record_error(span, ValueError("Invalid input"))
        """
        if transaction:
            transaction.record_exception(error)
            transaction.set_attribute("error", True)
            transaction.set_attribute("error.message", str(error))
            transaction.set_attribute("error.type", type(error).__name__)

    def record_metric(self, name: str, value: float, tags: dict[str, str] | None = None) -> None:
        """
        Registra una métrica personalizada.

        Parameters
        ----------
        name : str
            Nombre de la métrica.
        value : float
            Valor de la métrica.
        tags : Optional[Dict[str, str]], optional
            Tags para la métrica (default: None).

        Examples
        --------
        >>> provider.record_metric("response_time", 150.5, {"endpoint": "/api/users"})
        """
        # Para OpenTelemetry, las métricas se manejan por separado
        # Este método se puede extender para integrar con el sistema de métricas
        pass


class APMManager:
    """Gestor principal del sistema APM."""

    def __init__(self, config: APMConfig):
        """
        Inicializa el gestor APM.

        Parameters
        ----------
        config : APMConfig
            Configuración del sistema APM.

        Examples
        --------
        >>> config = APMConfig(service_name="my-api")
        >>> manager = APMManager(config)
        """
        self.config = config
        self.providers: list[BaseAPMProvider] = []
        self._initialized = False

    def add_provider(self, provider: BaseAPMProvider) -> None:
        """
        Añade un proveedor APM.

        Parameters
        ----------
        provider : BaseAPMProvider
            Proveedor APM a añadir.

        Examples
        --------
        >>> manager.add_provider(OpenTelemetryAPMProvider(config))
        """
        self.providers.append(provider)

    def initialize(self) -> None:
        """
        Inicializa todos los proveedores APM.

        Examples
        --------
        >>> manager.initialize()
        """
        if self._initialized or not self.config.enabled:
            return

        for provider in self.providers:
            with contextlib.suppress(Exception):
                provider.initialize()

        self._initialized = True

    def start_transaction(self, name: str, transaction_type: str = "web") -> list[Any]:
        """
        Inicia una transacción en todos los proveedores.

        Parameters
        ----------
        name : str
            Nombre de la transacción.
        transaction_type : str, optional
            Tipo de transacción (default: "web").

        Returns
        -------
        List[Any]
            Lista de transacciones de todos los proveedores.

        Examples
        --------
        >>> transactions = manager.start_transaction("/api/users", "web")
        """
        if not self._initialized:
            self.initialize()

        transactions = []
        for provider in self.providers:
            try:
                transaction = provider.start_transaction(name, transaction_type)
                if transaction:
                    transactions.append(transaction)
            except Exception:
                # Continuar con otros proveedores si uno falla
                pass

        return transactions

    def end_transaction(self, transactions: list[Any], status: str = "success") -> None:
        """
        Finaliza transacciones en todos los proveedores.

        Parameters
        ----------
        transactions : List[Any]
            Lista de transacciones a finalizar.
        status : str, optional
            Estado de las transacciones (default: "success").

        Examples
        --------
        >>> manager.end_transaction(transactions, "success")
        """
        for i, transaction in enumerate(transactions):
            if i < len(self.providers):
                with contextlib.suppress(Exception):
                    self.providers[i].end_transaction(transaction, status)

    def add_custom_attribute(self, transactions: list[Any], key: str, value: Any) -> None:
        """
        Añade un atributo personalizado a todas las transacciones.

        Parameters
        ----------
        transactions : List[Any]
            Lista de transacciones.
        key : str
            Clave del atributo.
        value : Any
            Valor del atributo.

        Examples
        --------
        >>> manager.add_custom_attribute(transactions, "user_id", "12345")
        """
        for i, transaction in enumerate(transactions):
            if i < len(self.providers):
                with contextlib.suppress(Exception):
                    self.providers[i].add_custom_attribute(transaction, key, value)

    def record_error(self, transactions: list[Any], error: Exception) -> None:
        """
        Registra un error en todas las transacciones.

        Parameters
        ----------
        transactions : List[Any]
            Lista de transacciones.
        error : Exception
            Error a registrar.

        Examples
        --------
        >>> manager.record_error(transactions, ValueError("Invalid input"))
        """
        for i, transaction in enumerate(transactions):
            if i < len(self.providers):
                with contextlib.suppress(Exception):
                    self.providers[i].record_error(transaction, error)

    def record_metric(self, name: str, value: float, tags: dict[str, str] | None = None) -> None:
        """
        Registra una métrica en todos los proveedores.

        Parameters
        ----------
        name : str
            Nombre de la métrica.
        value : float
            Valor de la métrica.
        tags : Optional[Dict[str, str]], optional
            Tags para la métrica (default: None).

        Examples
        --------
        >>> manager.record_metric("response_time", 150.5, {"endpoint": "/api/users"})
        """
        for provider in self.providers:
            with contextlib.suppress(Exception):
                provider.record_metric(name, value, tags)


# Funciones de conveniencia para compatibilidad con código existente
# Estas funciones están deprecadas y se recomienda usar inyección de dependencias


def configure_apm(config: APMConfig) -> APMManager:
    """
    Configura el sistema APM.

    Parameters
    ----------
    config : APMConfig
        Configuración del sistema APM.

    Returns
    -------
    APMManager
        Gestor APM configurado.

    Examples
    --------
    >>> config = APMConfig(service_name="my-api")
    >>> manager = configure_apm(config)

    Note
    ----
    Esta función está deprecada. Se recomienda usar inyección de dependencias
    a través del contenedor DI del framework.
    """
    manager = APMManager(config)

    # Añadir proveedor base OpenTelemetry
    manager.add_provider(OpenTelemetryAPMProvider(config))

    return manager


def get_apm_manager() -> APMManager:
    """
    Obtiene una nueva instancia del gestor APM.

    Returns
    -------
    APMManager
        Nueva instancia del gestor APM.

    Examples
    --------
    >>> manager = get_apm_manager()
    >>> transactions = manager.start_transaction("/api/users")

    Note
    ----
    Esta función está deprecada. Se recomienda usar inyección de dependencias
    a través del contenedor DI del framework.
    """
    config = APMConfig()
    return configure_apm(config)


def apm_transaction(
    name: str, transaction_type: str = "web"
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorador para instrumentar funciones con APM.

    Parameters
    ----------
    name : str
        Nombre de la transacción.
    transaction_type : str, optional
        Tipo de transacción (default: "web").

    Returns
    -------
    Callable
        Decorador de función.

    Examples
    --------
    >>> @apm_transaction("user_creation", "custom")
    ... def create_user(user_data):
    ...     # Lógica de creación de usuario
    ...     pass
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            manager = get_apm_manager()
            if not manager:
                return func(*args, **kwargs)

            transactions = manager.start_transaction(name, transaction_type)
            try:
                result = func(*args, **kwargs)
                manager.end_transaction(transactions, "success")
                return result
            except Exception as e:
                manager.record_error(transactions, e)
                manager.end_transaction(transactions, "error")
                raise

        return wrapper

    return decorator


def apm_async_transaction(
    name: str, transaction_type: str = "web"
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorador para instrumentar funciones async con APM.

    Parameters
    ----------
    name : str
        Nombre de la transacción.
    transaction_type : str, optional
        Tipo de transacción (default: "web").

    Returns
    -------
    Callable
        Decorador de función async.

    Examples
    --------
    >>> @apm_async_transaction("async_user_creation", "custom")
    ... async def create_user_async(user_data):
    ...     # Lógica asíncrona de creación de usuario
    ...     pass
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            manager = get_apm_manager()
            if not manager:
                return await func(*args, **kwargs)

            transactions = manager.start_transaction(name, transaction_type)
            try:
                result = await func(*args, **kwargs)
                manager.end_transaction(transactions, "success")
                return result
            except Exception as e:
                manager.record_error(transactions, e)
                manager.end_transaction(transactions, "error")
                raise

        return wrapper

    return decorator
