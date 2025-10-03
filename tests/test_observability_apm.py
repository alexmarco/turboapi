"""
Pruebas simplificadas para el sistema APM (Application Performance Monitoring).
"""

import time

import pytest

from turboapi.observability.apm import APMConfig
from turboapi.observability.apm import APMManager
from turboapi.observability.apm import BaseAPMProvider
from turboapi.observability.apm import OpenTelemetryAPMProvider
from turboapi.observability.apm import apm_async_transaction
from turboapi.observability.apm import apm_transaction
from turboapi.observability.apm import configure_apm
from turboapi.observability.apm import get_apm_manager


class TestAPMConfig:
    """Pruebas para APMConfig."""

    def test_apm_config_defaults(self):
        """Prueba los valores por defecto de APMConfig."""
        config = APMConfig()

        assert config.enabled is True
        assert config.service_name == "turboapi-app"
        assert config.environment == "development"
        assert config.version == "1.0.0"
        assert config.sample_rate == 1.0
        assert config.max_attributes == 128
        assert config.max_events == 128
        assert config.max_links == 128
        assert config.exporters == ["otlp"]
        # APM providers are now addons, not part of core config

    def test_apm_config_custom_values(self):
        """Prueba APMConfig con valores personalizados."""
        config = APMConfig(
            enabled=False,
            service_name="my-api",
            environment="production",
            version="2.1.0",
            sample_rate=0.5,
            max_attributes=256,
        )

        assert config.enabled is False
        assert config.service_name == "my-api"
        assert config.environment == "production"
        assert config.version == "2.1.0"
        assert config.sample_rate == 0.5
        assert config.max_attributes == 256
        # APM providers are now addons, not part of core config

    def test_apm_config_from_dict(self):
        """Prueba la creación de APMConfig desde diccionario."""
        data = {
            "enabled": True,
            "service_name": "test-api",
            "environment": "staging",
            "version": "1.5.0",
            "sample_rate": 0.8,
        }

        config = APMConfig.from_dict(data)

        assert config.enabled is True
        assert config.service_name == "test-api"
        assert config.environment == "staging"
        assert config.version == "1.5.0"
        assert config.sample_rate == 0.8


class TestBaseAPMProvider:
    """Pruebas para BaseAPMProvider."""

    def test_base_apm_provider_creation(self):
        """Prueba que BaseAPMProvider es abstracto."""
        config = APMConfig()

        # No se puede instanciar directamente
        with pytest.raises(TypeError):
            BaseAPMProvider(config)


class TestOpenTelemetryAPMProvider:
    """Pruebas para OpenTelemetryAPMProvider."""

    def test_open_telemetry_provider_creation(self):
        """Prueba la creación de OpenTelemetryAPMProvider."""
        config = APMConfig()
        provider = OpenTelemetryAPMProvider(config)

        assert provider.config == config
        assert provider._initialized is False
        assert provider._tracer_provider is None
        assert provider._tracer is None

    def test_open_telemetry_provider_initialize(self):
        """Prueba la inicialización de OpenTelemetryAPMProvider."""
        config = APMConfig()
        provider = OpenTelemetryAPMProvider(config)

        provider.initialize()

        assert provider._initialized is True
        assert provider._tracer_provider is not None
        assert provider._tracer is not None

    def test_open_telemetry_provider_start_transaction(self):
        """Prueba el inicio de transacción."""
        config = APMConfig()
        provider = OpenTelemetryAPMProvider(config)

        provider.initialize()
        transaction = provider.start_transaction("/api/users", "web")

        assert transaction is not None
        assert hasattr(transaction, "set_attribute")
        assert hasattr(transaction, "end")

    def test_open_telemetry_provider_end_transaction(self):
        """Prueba el final de transacción."""
        config = APMConfig()
        provider = OpenTelemetryAPMProvider(config)

        provider.initialize()
        transaction = provider.start_transaction("/api/users", "web")

        # No debería lanzar excepción
        provider.end_transaction(transaction, "success")

    def test_open_telemetry_provider_add_custom_attribute(self):
        """Prueba la adición de atributos personalizados."""
        config = APMConfig()
        provider = OpenTelemetryAPMProvider(config)

        provider.initialize()
        transaction = provider.start_transaction("/api/users", "web")

        # No debería lanzar excepción
        provider.add_custom_attribute(transaction, "user_id", "12345")

    def test_open_telemetry_provider_record_error(self):
        """Prueba el registro de errores."""
        config = APMConfig()
        provider = OpenTelemetryAPMProvider(config)

        provider.initialize()
        transaction = provider.start_transaction("/api/users", "web")

        error = ValueError("Test error")

        # No debería lanzar excepción
        provider.record_error(transaction, error)

    def test_open_telemetry_provider_record_metric(self):
        """Prueba el registro de métricas."""
        config = APMConfig()
        provider = OpenTelemetryAPMProvider(config)

        provider.initialize()

        # No debería lanzar excepción
        provider.record_metric("response_time", 150.5, {"endpoint": "/api/users"})


# Tests for NewRelic and DataDog providers moved to addons
# See test_addons_apm_newrelic.py and test_addons_apm_datadog.py


class TestAPMManager:
    """Pruebas para APMManager."""

    def test_apm_manager_creation(self):
        """Prueba la creación de APMManager."""
        config = APMConfig()
        manager = APMManager(config)

        assert manager.config == config
        assert manager.providers == []
        assert manager._initialized is False

    def test_apm_manager_add_provider(self):
        """Prueba la adición de proveedores."""
        config = APMConfig()
        manager = APMManager(config)

        provider = OpenTelemetryAPMProvider(config)
        manager.add_provider(provider)

        assert len(manager.providers) == 1
        assert provider in manager.providers

    def test_apm_manager_initialize(self):
        """Prueba la inicialización del gestor."""
        config = APMConfig()
        manager = APMManager(config)

        provider = OpenTelemetryAPMProvider(config)
        manager.add_provider(provider)

        manager.initialize()

        assert manager._initialized is True
        assert provider._initialized is True

    def test_apm_manager_initialize_disabled(self):
        """Prueba que no se inicialice cuando está deshabilitado."""
        config = APMConfig(enabled=False)
        manager = APMManager(config)

        provider = OpenTelemetryAPMProvider(config)
        manager.add_provider(provider)

        manager.initialize()

        assert manager._initialized is False
        assert provider._initialized is False

    def test_apm_manager_start_transaction(self):
        """Prueba el inicio de transacciones."""
        config = APMConfig()
        manager = APMManager(config)

        provider = OpenTelemetryAPMProvider(config)
        manager.add_provider(provider)

        transactions = manager.start_transaction("/api/users", "web")

        assert len(transactions) == 1
        assert transactions[0] is not None

    def test_apm_manager_end_transaction(self):
        """Prueba el final de transacciones."""
        config = APMConfig()
        manager = APMManager(config)

        provider = OpenTelemetryAPMProvider(config)
        manager.add_provider(provider)

        transactions = manager.start_transaction("/api/users", "web")

        # No debería lanzar excepción
        manager.end_transaction(transactions, "success")

    def test_apm_manager_add_custom_attribute(self):
        """Prueba la adición de atributos personalizados."""
        config = APMConfig()
        manager = APMManager(config)

        provider = OpenTelemetryAPMProvider(config)
        manager.add_provider(provider)

        transactions = manager.start_transaction("/api/users", "web")

        # No debería lanzar excepción
        manager.add_custom_attribute(transactions, "user_id", "12345")

    def test_apm_manager_record_error(self):
        """Prueba el registro de errores."""
        config = APMConfig()
        manager = APMManager(config)

        provider = OpenTelemetryAPMProvider(config)
        manager.add_provider(provider)

        transactions = manager.start_transaction("/api/users", "web")

        error = ValueError("Test error")

        # No debería lanzar excepción
        manager.record_error(transactions, error)

    def test_apm_manager_record_metric(self):
        """Prueba el registro de métricas."""
        config = APMConfig()
        manager = APMManager(config)

        provider = OpenTelemetryAPMProvider(config)
        manager.add_provider(provider)

        # No debería lanzar excepción
        manager.record_metric("response_time", 150.5, {"endpoint": "/api/users"})


class TestAPMIntegration:
    """Pruebas de integración para el sistema APM."""

    def test_configure_apm_function(self):
        """Prueba la función configure_apm."""
        config = APMConfig(service_name="test-api")
        manager = configure_apm(config)

        assert isinstance(manager, APMManager)
        assert manager.config == config
        assert len(manager.providers) == 1
        assert isinstance(manager.providers[0], OpenTelemetryAPMProvider)

    def test_configure_apm_core_only(self):
        """Prueba configure_apm solo con OpenTelemetry (core)."""
        config = APMConfig()
        manager = configure_apm(config)

        assert len(manager.providers) == 1
        assert isinstance(manager.providers[0], OpenTelemetryAPMProvider)

    def test_get_apm_manager_function(self):
        """Prueba la función get_apm_manager."""
        # Resetear el manager global
        import turboapi.observability.apm

        turboapi.observability.apm._apm_manager = None

        # Sin configurar - ahora devuelve una nueva instancia
        manager = get_apm_manager()
        assert manager is not None
        assert isinstance(manager, APMManager)

        # Configurar
        config = APMConfig()
        configured_manager = configure_apm(config)

        manager = get_apm_manager()
        # Ahora get_apm_manager() siempre retorna una nueva instancia
        assert isinstance(manager, APMManager)
        assert isinstance(configured_manager, APMManager)

    def test_apm_transaction_decorator(self):
        """Prueba el decorador apm_transaction."""
        config = APMConfig()
        configure_apm(config)

        @apm_transaction("test_function", "custom")
        def test_function(value):
            return value * 2

        result = test_function(5)
        assert result == 10

    def test_apm_transaction_decorator_with_error(self):
        """Prueba el decorador apm_transaction con error."""
        config = APMConfig()
        configure_apm(config)

        @apm_transaction("test_function_error", "custom")
        def test_function_error():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            test_function_error()

    @pytest.mark.asyncio
    async def test_apm_async_transaction_decorator(self):
        """Prueba el decorador apm_async_transaction."""
        config = APMConfig()
        configure_apm(config)

        @apm_async_transaction("test_async_function", "custom")
        async def test_async_function(value):
            return value * 2

        result = await test_async_function(5)
        assert result == 10

    @pytest.mark.asyncio
    async def test_apm_async_transaction_decorator_with_error(self):
        """Prueba el decorador apm_async_transaction con error."""
        config = APMConfig()
        configure_apm(config)

        @apm_async_transaction("test_async_function_error", "custom")
        async def test_async_function_error():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            await test_async_function_error()

    def test_apm_workflow_integration(self):
        """Prueba un flujo completo de trabajo con APM."""
        config = APMConfig(service_name="integration-test")
        manager = configure_apm(config)

        # Iniciar transacción
        transactions = manager.start_transaction("/api/test", "web")

        # Añadir atributos
        manager.add_custom_attribute(transactions, "user_id", "12345")
        manager.add_custom_attribute(transactions, "request_id", "req-123")

        # Simular procesamiento
        time.sleep(0.001)

        # Registrar métrica
        manager.record_metric("processing_time", 1.5, {"endpoint": "/api/test"})

        # Finalizar transacción
        manager.end_transaction(transactions, "success")

        assert len(transactions) == 1
        assert transactions[0] is not None
