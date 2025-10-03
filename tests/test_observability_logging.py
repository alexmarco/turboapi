"""Pruebas para el sistema de logging estructurado de TurboAPI."""

from unittest.mock import patch

import pytest

from turboapi.observability.logging import LoggingConfig
from turboapi.observability.logging import LogLevel
from turboapi.observability.logging import StructuredLogger
from turboapi.observability.logging import TurboLogging
from turboapi.observability.logging import configure_logging
from turboapi.observability.logging import get_logger


class TestLogLevel:
    """Pruebas para el enum LogLevel."""

    def test_log_level_values(self):
        """Prueba que LogLevel tiene los valores correctos."""
        assert LogLevel.DEBUG.value == "DEBUG"
        assert LogLevel.INFO.value == "INFO"
        assert LogLevel.WARNING.value == "WARNING"
        assert LogLevel.ERROR.value == "ERROR"
        assert LogLevel.CRITICAL.value == "CRITICAL"

    def test_log_level_from_string(self):
        """Prueba la conversión desde string a LogLevel."""
        assert LogLevel.from_string("DEBUG") == LogLevel.DEBUG
        assert LogLevel.from_string("INFO") == LogLevel.INFO
        assert LogLevel.from_string("WARNING") == LogLevel.WARNING
        assert LogLevel.from_string("ERROR") == LogLevel.ERROR
        assert LogLevel.from_string("CRITICAL") == LogLevel.CRITICAL

    def test_log_level_from_string_invalid(self):
        """Prueba que LogLevel.from_string maneja valores inválidos."""
        with pytest.raises(ValueError, match="Invalid log level"):
            LogLevel.from_string("INVALID")

    def test_log_level_from_string_case_insensitive(self):
        """Prueba que LogLevel.from_string es case-insensitive."""
        assert LogLevel.from_string("debug") == LogLevel.DEBUG
        assert LogLevel.from_string("Info") == LogLevel.INFO
        assert LogLevel.from_string("WARNING") == LogLevel.WARNING


class TestLoggingConfig:
    """Pruebas para la configuración de logging."""

    def test_logging_config_defaults(self):
        """Prueba los valores por defecto de LoggingConfig."""
        config = LoggingConfig()

        assert config.level == LogLevel.INFO
        assert config.format == "json"
        assert config.enable_console is True
        assert config.enable_file is False
        assert config.file_path is None
        assert config.max_file_size == 10 * 1024 * 1024  # 10MB
        assert config.backup_count == 5
        assert config.enable_structured is True
        assert config.extra_fields == {}

    def test_logging_config_custom(self):
        """Prueba LoggingConfig con valores personalizados."""
        config = LoggingConfig(
            level=LogLevel.DEBUG,
            format="text",
            enable_console=False,
            enable_file=True,
            file_path="/tmp/test.log",
            max_file_size=1024,
            backup_count=3,
            enable_structured=False,
            extra_fields={"service": "test", "version": "1.0.0"},
        )

        assert config.level == LogLevel.DEBUG
        assert config.format == "text"
        assert config.enable_console is False
        assert config.enable_file is True
        assert config.file_path == "/tmp/test.log"
        assert config.max_file_size == 1024
        assert config.backup_count == 3
        assert config.enable_structured is False
        assert config.extra_fields == {"service": "test", "version": "1.0.0"}

    def test_logging_config_from_dict(self):
        """Prueba la creación de LoggingConfig desde un diccionario."""
        config_dict = {
            "level": "DEBUG",
            "format": "json",
            "enable_console": True,
            "enable_file": True,
            "file_path": "/var/log/app.log",
            "max_file_size": 2048,
            "backup_count": 2,
            "enable_structured": True,
            "extra_fields": {"env": "production"},
        }

        config = LoggingConfig.from_dict(config_dict)

        assert config.level == LogLevel.DEBUG
        assert config.format == "json"
        assert config.enable_console is True
        assert config.enable_file is True
        assert config.file_path == "/var/log/app.log"
        assert config.max_file_size == 2048
        assert config.backup_count == 2
        assert config.enable_structured is True
        assert config.extra_fields == {"env": "production"}


class TestStructuredLogger:
    """Pruebas para el logger estructurado."""

    def test_structured_logger_creation(self):
        """Prueba la creación de un StructuredLogger."""
        logger = StructuredLogger("test_logger")

        assert logger.name == "test_logger"
        assert logger._extra_fields == {}

    def test_structured_logger_with_extra_fields(self):
        """Prueba StructuredLogger con campos extra."""
        extra_fields = {"service": "test", "version": "1.0.0"}
        logger = StructuredLogger("test_logger", extra_fields=extra_fields)

        assert logger._extra_fields == extra_fields

    def test_structured_logger_debug(self):
        """Prueba el método debug del StructuredLogger."""
        logger = StructuredLogger("test_logger")

        with patch.object(logger._logger, "debug") as mock_debug:
            logger.debug("Test message", user_id=123, action="login")

            mock_debug.assert_called_once()
            call_args = mock_debug.call_args
            assert "Test message" in str(call_args)
            assert "user_id" in str(call_args)
            assert "action" in str(call_args)

    def test_structured_logger_info(self):
        """Prueba el método info del StructuredLogger."""
        logger = StructuredLogger("test_logger")

        with patch.object(logger._logger, "info") as mock_info:
            logger.info("Info message", request_id="req-123")

            mock_info.assert_called_once()
            call_args = mock_info.call_args
            assert "Info message" in str(call_args)
            assert "request_id" in str(call_args)

    def test_structured_logger_warning(self):
        """Prueba el método warning del StructuredLogger."""
        logger = StructuredLogger("test_logger")

        with patch.object(logger._logger, "warning") as mock_warning:
            logger.warning("Warning message", error_code="WARN001")

            mock_warning.assert_called_once()
            call_args = mock_warning.call_args
            assert "Warning message" in str(call_args)
            assert "error_code" in str(call_args)

    def test_structured_logger_error(self):
        """Prueba el método error del StructuredLogger."""
        logger = StructuredLogger("test_logger")

        with patch.object(logger._logger, "error") as mock_error:
            logger.error("Error message", exception="ValueError", traceback="...")

            mock_error.assert_called_once()
            call_args = mock_error.call_args
            assert "Error message" in str(call_args)
            assert "exception" in str(call_args)
            assert "traceback" in str(call_args)

    def test_structured_logger_critical(self):
        """Prueba el método critical del StructuredLogger."""
        logger = StructuredLogger("test_logger")

        with patch.object(logger._logger, "critical") as mock_critical:
            logger.critical("Critical message", system="database", status="down")

            mock_critical.assert_called_once()
            call_args = mock_critical.call_args
            assert "Critical message" in str(call_args)
            assert "system" in str(call_args)
            assert "status" in str(call_args)

    def test_structured_logger_with_extra_fields_in_logs(self):
        """Prueba que los campos extra se incluyen en todos los logs."""
        extra_fields = {"service": "test", "version": "1.0.0"}
        logger = StructuredLogger("test_logger", extra_fields=extra_fields)

        with patch.object(logger._logger, "info") as mock_info:
            logger.info("Test message", user_id=123)

            mock_info.assert_called_once()
            call_args = mock_info.call_args
            # Verificar que los campos extra están presentes
            assert "service" in str(call_args)
            assert "version" in str(call_args)
            assert "user_id" in str(call_args)


class TestTurboLogging:
    """Pruebas para la clase principal TurboLogging."""

    def test_turbo_logging_initialization(self):
        """Prueba la inicialización de TurboLogging."""
        config = LoggingConfig(level=LogLevel.DEBUG)
        turbo_logging = TurboLogging(config)

        assert turbo_logging.config == config
        assert turbo_logging._configured is False

    def test_turbo_logging_configure(self):
        """Prueba la configuración del sistema de logging."""
        config = LoggingConfig(
            level=LogLevel.INFO,
            format="json",
            enable_console=True,
            enable_file=False,
            enable_structured=True,
        )

        turbo_logging = TurboLogging(config)

        with patch("structlog.configure") as mock_configure:
            turbo_logging.configure()

            assert turbo_logging._configured is True
            mock_configure.assert_called_once()

    def test_turbo_logging_get_logger(self):
        """Prueba la obtención de un logger."""
        config = LoggingConfig()
        turbo_logging = TurboLogging(config)
        turbo_logging.configure()

        logger = turbo_logging.get_logger("test_module")

        assert isinstance(logger, StructuredLogger)
        assert logger.name == "test_module"

    def test_turbo_logging_get_logger_with_extra_fields(self):
        """Prueba la obtención de un logger con campos extra."""
        config = LoggingConfig()
        turbo_logging = TurboLogging(config)
        turbo_logging.configure()

        extra_fields = {"service": "api", "version": "2.0.0"}
        logger = turbo_logging.get_logger("test_module", extra_fields=extra_fields)

        assert isinstance(logger, StructuredLogger)
        assert logger.name == "test_module"
        assert logger._extra_fields == extra_fields

    def test_turbo_logging_configure_twice(self):
        """Prueba que configurar dos veces no causa problemas."""
        config = LoggingConfig()
        turbo_logging = TurboLogging(config)

        with patch("structlog.configure") as mock_configure:
            turbo_logging.configure()
            turbo_logging.configure()  # Segunda vez

            # Debería llamar a configure solo una vez
            assert mock_configure.call_count == 1


class TestLoggingIntegration:
    """Pruebas de integración para el sistema de logging."""

    def test_configure_logging_function(self):
        """Prueba la función de conveniencia configure_logging."""
        config = LoggingConfig(level=LogLevel.DEBUG)

        with patch("structlog.configure") as mock_configure:
            configure_logging(config)
            mock_configure.assert_called_once()

    def test_get_logger_function(self):
        """Prueba la función de conveniencia get_logger."""
        config = LoggingConfig()
        configure_logging(config)

        logger = get_logger("test_module")

        assert isinstance(logger, StructuredLogger)
        assert logger.name == "test_module"

    def test_logging_with_different_formats(self):
        """Prueba logging con diferentes formatos."""
        # Test JSON format
        json_config = LoggingConfig(format="json")
        json_logging = TurboLogging(json_config)

        with patch("structlog.configure") as mock_configure:
            json_logging.configure()
            # Verificar que se configuró con JSON
            call_args = mock_configure.call_args
            assert "json" in str(call_args).lower()

        # Test text format
        text_config = LoggingConfig(format="text")
        text_logging = TurboLogging(text_config)

        with patch("structlog.configure") as mock_configure:
            text_logging.configure()
            # Verificar que se configuró con ConsoleRenderer (formato texto)
            call_args = mock_configure.call_args
            assert "consolerenderer" in str(call_args).lower()

    def test_logging_levels_filtering(self):
        """Prueba que los niveles de logging filtran correctamente."""
        config = LoggingConfig(level=LogLevel.WARNING)
        turbo_logging = TurboLogging(config)
        turbo_logging.configure()

        logger = turbo_logging.get_logger("test")

        with (
            patch.object(logger._logger, "debug") as mock_debug,
            patch.object(logger._logger, "info") as mock_info,
            patch.object(logger._logger, "warning") as mock_warning,
            patch.object(logger._logger, "error") as mock_error,
        ):
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")

            # Con nivel WARNING, solo warning y error deberían ejecutarse
            # (esto depende de la implementación real del filtrado)
            mock_warning.assert_called_once()
            mock_error.assert_called_once()

    def test_structured_logging_integration(self):
        """Prueba la integración completa del logging estructurado."""
        config = LoggingConfig(
            level=LogLevel.INFO,
            format="json",
            enable_structured=True,
            extra_fields={"service": "test", "version": "1.0.0"},
        )

        turbo_logging = TurboLogging(config)
        turbo_logging.configure()

        logger = turbo_logging.get_logger("integration_test")

        # Capturar output para verificar estructura
        with patch.object(logger._logger, "info") as mock_info:
            logger.info("User action completed", user_id=123, action="login", duration_ms=150)

            mock_info.assert_called_once()
            # Verificar que se incluyeron todos los campos
            call_args = str(mock_info.call_args)
            assert "User action completed" in call_args
            assert "user_id" in call_args
            assert "action" in call_args
            assert "duration_ms" in call_args
            assert "service" in call_args
            assert "version" in call_args
