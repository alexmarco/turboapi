"""Pruebas para el contenedor de inyección de dependencias."""

import pytest

from turboapi.core.di import ComponentProvider
from turboapi.core.di import TurboContainer


class SampleService:
    """Servicio de prueba para testing del contenedor DI."""

    def __init__(self) -> None:
        self.value = "test_value"


class SampleServiceWithDependency:
    """Servicio que depende de SampleService."""

    def __init__(self, sample_service: SampleService) -> None:
        self.sample_service = sample_service


class TestTurboContainer:
    """Pruebas para el contenedor de inyección de dependencias."""

    def test_register_singleton_component(self) -> None:
        """Prueba que se puede registrar un componente como singleton."""
        container = TurboContainer()

        # Registrar un componente
        container.register("sample_service", ComponentProvider(SampleService, singleton=True))

        # Verificar que está registrado
        assert container.is_registered("sample_service")

    def test_resolve_singleton_component(self) -> None:
        """Prueba que se puede resolver un componente singleton."""
        container = TurboContainer()

        # Registrar un componente como singleton
        container.register("sample_service", ComponentProvider(SampleService, singleton=True))

        # Resolver el componente
        instance1 = container.resolve_typed("sample_service", SampleService)
        instance2 = container.resolve_typed("sample_service", SampleService)

        # Verificar que es la misma instancia (singleton)
        assert instance1 is instance2
        assert instance1.value == "test_value"

    def test_resolve_transient_component(self) -> None:
        """Prueba que se pueden resolver múltiples instancias de un componente transient."""
        container = TurboContainer()

        # Registrar un componente como transient
        container.register("sample_service", ComponentProvider(SampleService, singleton=False))

        # Resolver el componente múltiples veces
        instance1 = container.resolve_typed("sample_service", SampleService)
        instance2 = container.resolve_typed("sample_service", SampleService)

        # Verificar que son instancias diferentes
        assert instance1 is not instance2

    def test_resolve_with_dependencies(self) -> None:
        """Prueba que se pueden resolver dependencias transitivas."""
        container = TurboContainer()

        # Registrar dependencia
        container.register("sample_service", ComponentProvider(SampleService, singleton=True))

        # Registrar servicio que depende de SampleService
        container.register(
            "sample_service_with_dependency",
            ComponentProvider(SampleServiceWithDependency, singleton=True),
        )

        # Resolver el servicio con dependencia
        instance = container.resolve_typed(
            "sample_service_with_dependency", SampleServiceWithDependency
        )

        # Verificar que la dependencia fue inyectada correctamente
        assert isinstance(instance.sample_service, SampleService)
        assert instance.sample_service.value == "test_value"

    def test_resolve_unregistered_component_raises_error(self) -> None:
        """Prueba que resolver un componente no registrado lanza una excepción."""
        container = TurboContainer()

        with pytest.raises(ValueError, match="Component 'unregistered' not found"):
            container.resolve("unregistered")

    def test_register_duplicate_component_raises_error(self) -> None:
        """Prueba que registrar un componente duplicado lanza una excepción."""
        container = TurboContainer()

        # Registrar un componente
        container.register("sample_service", ComponentProvider(SampleService, singleton=True))

        # Intentar registrar el mismo componente otra vez
        with pytest.raises(ValueError, match="Component 'sample_service' is already registered"):
            container.register("sample_service", ComponentProvider(SampleService, singleton=True))

    def test_resolve_typed_with_wrong_type_raises_error(self) -> None:
        """Prueba que resolve_typed lanza error si el tipo no coincide."""
        container = TurboContainer()

        # Registrar un componente
        container.register("sample_service", ComponentProvider(SampleService, singleton=True))

        # Intentar resolver con un tipo incorrecto
        with pytest.raises(TypeError, match="Component 'sample_service' is not of expected type"):
            container.resolve_typed("sample_service", SampleServiceWithDependency)
