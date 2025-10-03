"""Aplicación principal del framework TurboAPI que integra todos los componentes del núcleo."""

from pathlib import Path
from typing import Any

from .config import TurboConfig
from .di import ComponentProvider
from .di import TurboContainer
from .discovery import ComponentScanner


class TurboApplication:
    """Aplicación principal del framework que integra configuración, DI y descubrimiento."""

    def __init__(self, pyproject_path: Path) -> None:
        """Inicializa la aplicación con la ruta al archivo pyproject.toml."""
        self.pyproject_path = pyproject_path
        self.config = TurboConfig.from_pyproject(pyproject_path)
        self.container = TurboContainer()
        self.scanner = ComponentScanner(self.config)
        self._initialized = False

    def initialize(self) -> None:
        """Inicializa la aplicación registrando todos los componentes."""
        if self._initialized:
            return

        # Registrar la configuración como singleton
        self.container.register("config", ComponentProvider(lambda: self.config, singleton=True))

        # Registrar el escáner como singleton
        self.container.register("scanner", ComponentProvider(lambda: self.scanner, singleton=True))

        # Registrar el contenedor como singleton
        self.container.register(
            "container", ComponentProvider(lambda: self.container, singleton=True)
        )

        # Escanear y registrar componentes de las aplicaciones instaladas
        self._register_discovered_components()

        self._initialized = True

    def _register_discovered_components(self) -> None:
        """Registra todos los componentes descubiertos en el contenedor DI."""
        # Limpiar el cache del escáner para asegurar que escanee todos los módulos
        temp_scanned_modules = self.scanner._scanned_modules.copy()
        self.scanner._scanned_modules.clear()

        try:
            components = self.scanner.scan_installed_apps()

            for component in components:
                # Generar un nombre único para el componente
                component_name = self._generate_component_name(component)

                # Registrar como singleton por defecto
                self.container.register(
                    component_name, ComponentProvider(component, singleton=True)
                )
        finally:
            # Restaurar el cache
            self.scanner._scanned_modules = temp_scanned_modules

    def _generate_component_name(self, component: Any) -> str:
        """Genera un nombre único para un componente."""
        if hasattr(component, "__module__") and hasattr(component, "__name__"):
            # Si el módulo es un módulo de prueba, usar el nombre de la clase directamente
            if "test_" in component.__module__:
                return component.__name__  # type: ignore[no-any-return]
            return f"{component.__module__}.{component.__name__}"
        else:
            # Fallback para componentes sin módulo/nombre claro
            return f"component_{id(component)}"

    def get_component(self, name: str) -> Any:
        """Obtiene un componente del contenedor DI."""
        if not self._initialized:
            self.initialize()
        return self.container.resolve(name)

    def get_component_typed(self, name: str, expected_type: type[Any]) -> Any:
        """Obtiene un componente del contenedor DI con verificación de tipo."""
        if not self._initialized:
            self.initialize()
        return self.container.resolve_typed(name, expected_type)

    def get_config(self) -> TurboConfig:
        """Obtiene la configuración de la aplicación."""
        return self.get_component_typed("config", TurboConfig)  # type: ignore[no-any-return]

    def get_scanner(self) -> ComponentScanner:
        """Obtiene el escáner de componentes."""
        return self.get_component_typed("scanner", ComponentScanner)  # type: ignore[no-any-return]

    def get_container(self) -> TurboContainer:
        """Obtiene el contenedor de inyección de dependencias."""
        return self.get_component_typed("container", TurboContainer)  # type: ignore[no-any-return]
