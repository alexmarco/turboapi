"""Sistema de descubrimiento de componentes del framework TurboAPI."""

import importlib
import inspect
from pathlib import Path
from typing import Any
from typing import TypeVar

from .config import TurboConfig

T = TypeVar("T")


class ComponentScanner:
    """Escáner de componentes para descubrir clases y funciones en las aplicaciones instaladas."""

    def __init__(self, config: TurboConfig) -> None:
        """Inicializa el escáner con la configuración del proyecto."""
        self.config = config
        self._scanned_modules: set[str] = set()

    def scan_installed_apps(self) -> list[Any]:
        """Escanea todas las aplicaciones instaladas y devuelve los componentes encontrados."""
        components: list[Any] = []

        for app_name in self.config.installed_apps:
            try:
                app_components = self._scan_app(app_name)
                components.extend(app_components)
            except ImportError as e:
                # Log warning but continue with other apps
                print(f"Warning: Could not import app '{app_name}': {e}")
                continue

        return components

    def _scan_app(self, app_name: str) -> list[Any]:
        """Escanea una aplicación específica y devuelve sus componentes."""
        components: list[Any] = []

        try:
            # Importar el módulo principal de la aplicación
            app_module = importlib.import_module(app_name)
            components.extend(self._scan_module(app_module))

            # Escanear submódulos si existen
            app_path = Path(app_module.__file__).parent if app_module.__file__ else None
            if app_path:
                components.extend(self._scan_app_directory(app_path, app_name))

        except ImportError as e:
            raise ImportError(f"Could not import app '{app_name}': {e}") from e

        return components

    def _scan_app_directory(self, app_path: Path, app_name: str) -> list[Any]:
        """Escanea un directorio de aplicación en busca de submódulos."""
        components: list[Any] = []

        # Buscar archivos Python en el directorio
        for py_file in app_path.glob("*.py"):
            if py_file.name.startswith("__"):
                continue

            module_name = f"{app_name}.{py_file.stem}"
            try:
                module = importlib.import_module(module_name)
                components.extend(self._scan_module(module))
            except ImportError:
                # Ignorar módulos que no se pueden importar
                continue

        return components

    def _scan_module(self, module: Any) -> list[Any]:
        """Escanea un módulo en busca de componentes."""
        if module.__name__ in self._scanned_modules:
            return []

        self._scanned_modules.add(module.__name__)
        components: list[Any] = []

        # Obtener todos los atributos del módulo
        for attr_name in dir(module):
            if attr_name.startswith("_"):
                continue

            attr = getattr(module, attr_name)

            # Verificar si es una clase
            if inspect.isclass(attr) or inspect.isfunction(attr):
                components.append(attr)

        return components

    def find_components_by_type(self, component_type: type[T]) -> list[T]:
        """Encuentra todos los componentes de un tipo específico."""
        # Usar una lista temporal para evitar problemas con el cache
        temp_scanned_modules = self._scanned_modules.copy()
        self._scanned_modules.clear()

        try:
            all_components = self.scan_installed_apps()
            return [comp for comp in all_components if isinstance(comp, component_type)]
        finally:
            # Restaurar el cache
            self._scanned_modules = temp_scanned_modules

    def find_components_with_decorator(self, decorator_name: str) -> list[Any]:
        """Encuentra todos los componentes que tienen un decorador específico."""
        # Usar una lista temporal para evitar problemas con el cache
        temp_scanned_modules = self._scanned_modules.copy()
        self._scanned_modules.clear()

        try:
            all_components = self.scan_installed_apps()
            decorated_components: list[Any] = []

            for component in all_components:
                # Verificar si el componente tiene el atributo que indica el decorador
                if hasattr(component, "_decorator_name"):
                    component_decorator = component._decorator_name
                    if component_decorator == decorator_name:
                        decorated_components.append(component)

            return decorated_components
        finally:
            # Restaurar el cache
            self._scanned_modules = temp_scanned_modules

    def find_controllers(self) -> list[type]:
        """Encuentra todas las clases marcadas como controladores."""
        # Usar una lista temporal para evitar problemas con el cache
        temp_scanned_modules = self._scanned_modules.copy()
        self._scanned_modules.clear()

        try:
            all_components = self.scan_installed_apps()
            controllers: list[type] = []

            for component in all_components:
                # Verificar si es una clase y si está marcada como controlador
                if (
                    inspect.isclass(component)
                    and hasattr(component, "_is_controller")
                    and component._is_controller
                ):
                    controllers.append(component)

            return controllers
        finally:
            # Restaurar el cache
            self._scanned_modules = temp_scanned_modules

    def find_endpoints_in_controller(self, controller_class: type) -> list[tuple[str, str, Any]]:
        """
        Encuentra todos los endpoints en una clase controlador.

        Returns:
            Lista de tuplas (método_http, ruta, función)
        """
        endpoints: list[tuple[str, str, Any]] = []

        for attr_name in dir(controller_class):
            if attr_name.startswith("_"):
                continue

            attr = getattr(controller_class, attr_name)

            # Verificar si es un método y si está marcado como endpoint
            if callable(attr) and hasattr(attr, "_is_endpoint") and attr._is_endpoint:
                http_method = getattr(attr, "_http_method", "GET")
                endpoint_path = getattr(attr, "_endpoint_path", "")
                endpoints.append((http_method, endpoint_path, attr))

        return endpoints

    def find_repositories(self) -> list[type]:
        """
        Encuentra todas las clases marcadas con @Repository.

        Returns:
            Lista de clases de repositorios
        """
        repositories = []

        for app_name in self.config.installed_apps:
            try:
                app_module = importlib.import_module(app_name)

                # Buscar repositorios directamente en el módulo principal
                for _name, obj in inspect.getmembers(app_module, inspect.isclass):
                    if hasattr(obj, "_is_repository") and getattr(obj, "_is_repository", False):
                        repositories.append(obj)

                # También buscar en subdirectorios si es un paquete
                app_path = Path(app_module.__file__).parent if app_module.__file__ else None

                if app_path and app_path.is_dir():
                    # Buscar en todos los archivos Python del directorio de la app
                    for py_file in app_path.rglob("*.py"):
                        if py_file.name.startswith("__"):
                            continue

                        module_name = f"{app_name}.{py_file.stem}"
                        try:
                            module = importlib.import_module(module_name)

                            # Buscar clases en el módulo
                            for _name, obj in inspect.getmembers(module, inspect.isclass):
                                if hasattr(obj, "_is_repository") and getattr(
                                    obj, "_is_repository", False
                                ):
                                    repositories.append(obj)

                        except ImportError:
                            continue

            except ImportError:
                continue

        return repositories

    def find_tasks(self) -> list[Any]:
        """
        Encuentra todas las funciones marcadas con el decorador @Task.

        Returns:
            Lista de funciones de tarea.
        """
        tasks = []

        for app_name in self.config.installed_apps:
            try:
                app_module = importlib.import_module(app_name)

                # Buscar tareas directamente en el módulo principal
                for _name, obj in inspect.getmembers(app_module):
                    if (
                        (inspect.isfunction(obj) or inspect.ismethod(obj))
                        and hasattr(obj, "_is_task")
                        and getattr(obj, "_is_task", False)
                    ):
                        tasks.append(obj)

                # También buscar en subdirectorios si es un paquete
                app_path = Path(app_module.__file__).parent if app_module.__file__ else None

                if app_path and app_path.is_dir():
                    # Buscar en todos los archivos Python del directorio de la app
                    for py_file in app_path.rglob("*.py"):
                        if py_file.name.startswith("__"):
                            continue

                        module_name = f"{app_name}.{py_file.stem}"
                        try:
                            module = importlib.import_module(module_name)

                            # Buscar funciones en el módulo
                            for _name, obj in inspect.getmembers(module):
                                if (
                                    (inspect.isfunction(obj) or inspect.ismethod(obj))
                                    and hasattr(obj, "_is_task")
                                    and getattr(obj, "_is_task", False)
                                ):
                                    tasks.append(obj)

                        except ImportError:
                            continue

            except ImportError:
                continue

        return tasks

    def find_cached_functions(self) -> list[Any]:
        """
        Encuentra todas las funciones marcadas con el decorador @Cache.

        Returns:
            Lista de funciones cacheables.
        """
        cached_functions = []

        for app_name in self.config.installed_apps:
            try:
                app_module = importlib.import_module(app_name)

                # Buscar funciones cacheables directamente en el módulo principal
                for _name, obj in inspect.getmembers(app_module):
                    if (
                        (inspect.isfunction(obj) or inspect.ismethod(obj))
                        and hasattr(obj, "_is_cached")
                        and getattr(obj, "_is_cached", False)
                    ):
                        cached_functions.append(obj)

                # También buscar en subdirectorios si es un paquete
                app_path = Path(app_module.__file__).parent if app_module.__file__ else None

                if app_path and app_path.is_dir():
                    # Buscar en todos los archivos Python del directorio de la app
                    for py_file in app_path.rglob("*.py"):
                        if py_file.name.startswith("__"):
                            continue

                        module_name = f"{app_name}.{py_file.stem}"
                        try:
                            module = importlib.import_module(module_name)

                            # Buscar funciones en el módulo
                            for _name, obj in inspect.getmembers(module):
                                if (
                                    (inspect.isfunction(obj) or inspect.ismethod(obj))
                                    and hasattr(obj, "_is_cached")
                                    and getattr(obj, "_is_cached", False)
                                ):
                                    cached_functions.append(obj)

                        except ImportError:
                            continue

            except ImportError:
                continue

        return cached_functions
