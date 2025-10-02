"""Sistema de inyección de dependencias del framework TurboAPI."""

import inspect
from collections.abc import Callable
from typing import Any
from typing import Generic
from typing import TypeVar

T = TypeVar("T")


class ComponentProvider(Generic[T]):
    """Proveedor de componentes para el contenedor DI."""

    def __init__(self, component: type[T] | Callable[[], T], singleton: bool = True) -> None:
        self.component = component
        self.singleton = singleton
        self._instance: T | None = None

    def get_instance(self, container: "TurboContainer") -> T:
        """Obtiene una instancia del componente."""
        if self.singleton:
            if self._instance is None:
                self._instance = self._create_instance(container)
            return self._instance
        else:
            return self._create_instance(container)

    def _create_instance(self, container: "TurboContainer") -> T:
        """Crea una nueva instancia del componente."""
        # Si es un callable (factory function), simplemente lo llamamos
        if callable(self.component) and not inspect.isclass(self.component):
            return self.component()

        # Si es una clase, usamos inyección de dependencias
        component_class = self.component
        signature = inspect.signature(component_class.__init__)

        # Preparar argumentos para el constructor
        kwargs: dict[str, Any] = {}

        for param_name, param in signature.parameters.items():
            if param_name == "self":
                continue

            # Obtener el tipo de la dependencia
            param_type = param.annotation

            # Si no tiene tipo, no podemos inyectar
            if param_type == inspect.Parameter.empty:
                raise ValueError(
                    f"Parameter '{param_name}' in {component_class.__name__} has no type annotation"
                )

            # Resolver la dependencia del contenedor
            # Buscar el componente por tipo directamente
            dependency_name = None
            for name, provider in container._providers.items():
                if hasattr(provider, "component") and provider.component == param_type:
                    dependency_name = name
                    break

            if dependency_name is None:
                raise ValueError(f"No registered component found for type {param_type.__name__}")

            kwargs[param_name] = container.resolve(dependency_name)

        return component_class(**kwargs)  # type: ignore[no-any-return]


class TurboContainer:
    """Contenedor de inyección de dependencias."""

    def __init__(self) -> None:
        self._providers: dict[str, ComponentProvider[Any]] = {}

    def register(self, name: str, provider: ComponentProvider[Any]) -> None:
        """Registra un proveedor de componente."""
        if name in self._providers:
            raise ValueError(f"Component '{name}' is already registered")

        self._providers[name] = provider

    def resolve(self, name: str) -> Any:
        """Resuelve un componente por nombre."""
        if name not in self._providers:
            raise ValueError(f"Component '{name}' not found")

        provider = self._providers[name]
        return provider.get_instance(self)

    def resolve_typed(self, name: str, expected_type: type[T]) -> T:
        """Resuelve un componente por nombre con verificación de tipo."""
        instance = self.resolve(name)
        if not isinstance(instance, expected_type):
            raise TypeError(f"Component '{name}' is not of expected type {expected_type.__name__}")
        return instance

    def is_registered(self, name: str) -> bool:
        """Verifica si un componente está registrado."""
        return name in self._providers
