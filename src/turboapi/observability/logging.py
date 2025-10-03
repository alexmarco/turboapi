"""Sistema de logging estructurado para TurboAPI."""

import logging
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any

import structlog


class LogLevel(Enum):
    """Niveles de logging disponibles."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    @classmethod
    def from_string(cls, level: str) -> "LogLevel":
        """
        Convierte un string a LogLevel.

        Parameters
        ----------
        level : str
            Nivel de logging como string.

        Returns
        -------
        LogLevel
            Nivel de logging correspondiente.

        Raises
        ------
        ValueError
            Si el nivel no es válido.

        Examples
        --------
        >>> LogLevel.from_string("DEBUG")
        <LogLevel.DEBUG: 'DEBUG'>
        >>> LogLevel.from_string("info")
        <LogLevel.INFO: 'INFO'>
        """
        level_upper = level.upper()
        for log_level in cls:
            if log_level.value == level_upper:
                return log_level
        raise ValueError(f"Invalid log level: {level}")


@dataclass
class LoggingConfig:
    """Configuración para el sistema de logging."""

    level: LogLevel = LogLevel.INFO
    format: str = "json"  # "json" o "text"
    enable_console: bool = True
    enable_file: bool = False
    file_path: str | None = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_structured: bool = True
    extra_fields: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "LoggingConfig":
        """
        Crea LoggingConfig desde un diccionario.

        Parameters
        ----------
        config_dict : Dict[str, Any]
            Diccionario de configuración.

        Returns
        -------
        LoggingConfig
            Configuración de logging.

        Examples
        --------
        >>> config = LoggingConfig.from_dict({
        ...     "level": "DEBUG",
        ...     "format": "json",
        ...     "enable_console": True
        ... })
        """
        # Convertir level string a LogLevel si es necesario
        level = config_dict.get("level", LogLevel.INFO)
        if isinstance(level, str):
            level = LogLevel.from_string(level)

        return cls(
            level=level,
            format=config_dict.get("format", "json"),
            enable_console=config_dict.get("enable_console", True),
            enable_file=config_dict.get("enable_file", False),
            file_path=config_dict.get("file_path"),
            max_file_size=config_dict.get("max_file_size", 10 * 1024 * 1024),
            backup_count=config_dict.get("backup_count", 5),
            enable_structured=config_dict.get("enable_structured", True),
            extra_fields=config_dict.get("extra_fields", {}),
        )


class StructuredLogger:
    """Logger estructurado que extiende las capacidades de logging estándar."""

    def __init__(self, name: str, extra_fields: dict[str, Any] | None = None):
        """
        Inicializa el logger estructurado.

        Parameters
        ----------
        name : str
            Nombre del logger.
        extra_fields : Dict[str, Any], optional
            Campos adicionales que se incluirán en todos los logs.

        Examples
        --------
        >>> logger = StructuredLogger("my_module")
        >>> logger.info("User logged in", user_id=123)
        """
        self.name = name
        self._extra_fields = extra_fields or {}
        self._logger = structlog.get_logger(name)

    def _merge_fields(self, **kwargs: Any) -> dict[str, Any]:
        """
        Combina campos extra con campos específicos del log.

        Parameters
        ----------
        **kwargs : Any
            Campos específicos del log.

        Returns
        -------
        Dict[str, Any]
            Campos combinados.
        """
        merged = self._extra_fields.copy()
        merged.update(kwargs)
        return merged

    def debug(self, message: str, **kwargs: Any) -> None:
        """
        Log a nivel DEBUG.

        Parameters
        ----------
        message : str
            Mensaje de log.
        **kwargs : Any
            Campos adicionales estructurados.

        Examples
        --------
        >>> logger.debug("Processing request", request_id="req-123", method="GET")
        """
        fields = self._merge_fields(**kwargs)
        self._logger.debug(message, **fields)

    def info(self, message: str, **kwargs: Any) -> None:
        """
        Log a nivel INFO.

        Parameters
        ----------
        message : str
            Mensaje de log.
        **kwargs : Any
            Campos adicionales estructurados.

        Examples
        --------
        >>> logger.info("User action", user_id=123, action="login")
        """
        fields = self._merge_fields(**kwargs)
        self._logger.info(message, **fields)

    def warning(self, message: str, **kwargs: Any) -> None:
        """
        Log a nivel WARNING.

        Parameters
        ----------
        message : str
            Mensaje de log.
        **kwargs : Any
            Campos adicionales estructurados.

        Examples
        --------
        >>> logger.warning("Rate limit exceeded", user_id=123, limit=100)
        """
        fields = self._merge_fields(**kwargs)
        self._logger.warning(message, **fields)

    def error(self, message: str, **kwargs: Any) -> None:
        """
        Log a nivel ERROR.

        Parameters
        ----------
        message : str
            Mensaje de log.
        **kwargs : Any
            Campos adicionales estructurados.

        Examples
        --------
        >>> logger.error("Database connection failed", error="timeout", retries=3)
        """
        fields = self._merge_fields(**kwargs)
        self._logger.error(message, **fields)

    def critical(self, message: str, **kwargs: Any) -> None:
        """
        Log a nivel CRITICAL.

        Parameters
        ----------
        message : str
            Mensaje de log.
        **kwargs : Any
            Campos adicionales estructurados.

        Examples
        --------
        >>> logger.critical("System failure", component="database", status="down")
        """
        fields = self._merge_fields(**kwargs)
        self._logger.critical(message, **fields)


class TurboLogging:
    """Sistema principal de logging de TurboAPI."""

    def __init__(self, config: LoggingConfig):
        """
        Inicializa el sistema de logging.

        Parameters
        ----------
        config : LoggingConfig
            Configuración del sistema de logging.

        Examples
        --------
        >>> config = LoggingConfig(level=LogLevel.DEBUG)
        >>> logging_system = TurboLogging(config)
        """
        self.config = config
        self._configured = False

    def configure(self) -> None:
        """
        Configura el sistema de logging usando structlog.

        Examples
        --------
        >>> config = LoggingConfig(level=LogLevel.INFO)
        >>> logging_system = TurboLogging(config)
        >>> logging_system.configure()
        """
        if self._configured:
            return

        # Configurar structlog
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
        ]

        if self.config.enable_structured:
            if self.config.format == "json":
                processors.append(structlog.processors.JSONRenderer())
            else:
                processors.append(structlog.dev.ConsoleRenderer())
        else:
            processors.append(structlog.dev.ConsoleRenderer())

        structlog.configure(
            processors=processors,  # type: ignore[arg-type]
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        # Configure standard logging
        logging.basicConfig(
            level=getattr(logging, self.config.level.value), format="%(message)s", force=True
        )

        self._configured = True

    def get_logger(self, name: str, extra_fields: dict[str, Any] | None = None) -> StructuredLogger:
        """
        Obtiene un logger estructurado.

        Parameters
        ----------
        name : str
            Nombre del logger.
        extra_fields : Dict[str, Any], optional
            Campos adicionales que se incluirán en todos los logs.

        Returns
        -------
        StructuredLogger
            Logger estructurado configurado.

        Examples
        --------
        >>> config = LoggingConfig()
        >>> logging_system = TurboLogging(config)
        >>> logging_system.configure()
        >>> logger = logging_system.get_logger("my_module")
        """
        if not self._configured:
            self.configure()

        # Combine extra fields from configuration with specific ones
        combined_extra_fields = self.config.extra_fields.copy()
        if extra_fields:
            combined_extra_fields.update(extra_fields)

        return StructuredLogger(name, combined_extra_fields)


# Convenience functions for compatibility with existing code
# These functions are deprecated and dependency injection is recommended


def configure_logging(config: LoggingConfig) -> TurboLogging:
    """
    Configura el sistema de logging.

    Parameters
    ----------
    config : LoggingConfig
        Configuración del sistema de logging.

    Returns
    -------
    TurboLogging
        Instancia del sistema de logging configurado.

    Examples
    --------
    >>> config = LoggingConfig(level=LogLevel.DEBUG, format="json")
    >>> logging_system = configure_logging(config)

    Note
    ----
    Esta función está deprecada. Se recomienda usar inyección de dependencias
    a través del contenedor DI del framework.
    """
    logging_system = TurboLogging(config)
    logging_system.configure()
    return logging_system


def get_logger(name: str, extra_fields: dict[str, Any] | None = None) -> StructuredLogger:
    """
    Obtiene un logger del sistema de logging.

    Parameters
    ----------
    name : str
        Nombre del logger.
    extra_fields : Dict[str, Any], optional
        Campos adicionales que se incluirán en todos los logs.

    Returns
    -------
    StructuredLogger
        Logger estructurado.

    Examples
    --------
    >>> logger = get_logger("my_module")
    >>> logger.info("Application started")

    Note
    ----
    Esta función está deprecada. Se recomienda usar inyección de dependencias
    a través del contenedor DI del framework.
    """
    # Crear una instancia temporal para compatibilidad
    config = LoggingConfig()
    logging_system = TurboLogging(config)
    logging_system.configure()
    return logging_system.get_logger(name, extra_fields)
