"""Sistema de enrutamiento para la capa web del framework TurboAPI."""

import functools
from collections.abc import Sequence
from typing import Any

from fastapi import FastAPI

from ..core.application import TurboApplication
from .utils import get_controller_metadata
from .utils import get_endpoint_metadata


class TurboAPI:
    """Clase principal para crear aplicaciones web con TurboAPI."""

    def __init__(self, application: TurboApplication) -> None:
        """
        Inicializa TurboAPI con una aplicación TurboAPI.

        Args:
            application: Instancia de TurboApplication configurada
        """
        self.application = application
        self.fastapi_app = FastAPI(
            title=application.config.project_name,
            version=application.config.project_version,
        )
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Configura las rutas basándose en los controladores descubiertos."""
        scanner = self.application.get_scanner()
        controllers = scanner.find_controllers()

        for controller_class in controllers:
            self._register_controller(controller_class)

    def _register_controller(self, controller_class: type) -> None:
        """
        Registra un controlador y sus endpoints en FastAPI.

        Args:
            controller_class: Clase del controlador a registrar
        """
        # Obtener metadatos del controlador de manera type-safe
        controller_metadata = get_controller_metadata(controller_class)
        controller_prefix = controller_metadata["prefix"]
        controller_tags = controller_metadata["tags"]
        controller_dependencies = controller_metadata["dependencies"]

        # Crear una instancia del controlador usando el contenedor DI
        controller_name = self._get_controller_name(controller_class)
        controller_instance = self.application.get_component(controller_name)

        # Obtener todos los endpoints del controlador
        scanner = self.application.get_scanner()
        endpoints = scanner.find_endpoints_in_controller(controller_class)

        # Registrar cada endpoint
        for http_method, endpoint_path, endpoint_func in endpoints:
            self._register_endpoint(
                controller_instance,
                endpoint_func,
                http_method,
                controller_prefix + endpoint_path,
                controller_tags,
                controller_dependencies,
            )

    def _register_endpoint(
        self,
        controller_instance: Any,
        endpoint_func: Any,
        http_method: str,
        full_path: str,
        controller_tags: Sequence[str],
        controller_dependencies: list[Any],
    ) -> None:
        """
        Registra un endpoint individual en FastAPI.

        Args:
            controller_instance: Instancia del controlador
            endpoint_func: Función del endpoint
            http_method: Método HTTP (GET, POST, etc.)
            full_path: Ruta completa del endpoint
            controller_tags: Etiquetas del controlador
            controller_dependencies: Dependencias del controlador
        """
        # Obtener metadatos del endpoint de manera type-safe
        endpoint_metadata = get_endpoint_metadata(endpoint_func)
        endpoint_tags = endpoint_metadata["tags"]
        endpoint_summary = endpoint_metadata["summary"]
        endpoint_description = endpoint_metadata["description"]
        endpoint_dependencies = endpoint_metadata["dependencies"]
        response_model = endpoint_metadata["response_model"]
        status_code = endpoint_metadata["status_code"]

        # Combinar etiquetas del controlador y del endpoint
        all_tags = list(controller_tags) + list(endpoint_tags)

        # Combinar dependencias del controlador y del endpoint
        all_dependencies = controller_dependencies + endpoint_dependencies

        # Crear el método del endpoint que llama a la instancia del controlador
        # Usar functools.partial para bindear el self
        endpoint_wrapper = functools.partial(endpoint_func, controller_instance)

        # Registrar el endpoint en FastAPI
        if http_method == "GET":
            self.fastapi_app.get(
                full_path,
                tags=all_tags,  # type: ignore[arg-type]
                summary=endpoint_summary,
                description=endpoint_description,
                dependencies=all_dependencies,
                response_model=response_model,
                status_code=status_code,
            )(endpoint_wrapper)
        elif http_method == "POST":
            self.fastapi_app.post(
                full_path,
                tags=all_tags,  # type: ignore[arg-type]
                summary=endpoint_summary,
                description=endpoint_description,
                dependencies=all_dependencies,
                response_model=response_model,
                status_code=status_code,
            )(endpoint_wrapper)
        elif http_method == "PUT":
            self.fastapi_app.put(
                full_path,
                tags=all_tags,  # type: ignore[arg-type]
                summary=endpoint_summary,
                description=endpoint_description,
                dependencies=all_dependencies,
                response_model=response_model,
                status_code=status_code,
            )(endpoint_wrapper)
        elif http_method == "DELETE":
            self.fastapi_app.delete(
                full_path,
                tags=all_tags,  # type: ignore[arg-type]
                summary=endpoint_summary,
                description=endpoint_description,
                dependencies=all_dependencies,
                response_model=response_model,
                status_code=status_code,
            )(endpoint_wrapper)

    def _get_controller_name(self, controller_class: type) -> str:
        """
        Obtiene el nombre del controlador para resolverlo del contenedor DI.

        Args:
            controller_class: Clase del controlador

        Returns:
            Nombre del controlador en el contenedor DI
        """
        # Usar la misma lógica que en TurboApplication
        if hasattr(controller_class, "__module__") and hasattr(controller_class, "__name__"):
            if "test_" in controller_class.__module__:
                return controller_class.__name__
            return f"{controller_class.__module__}.{controller_class.__name__}"
        else:
            return f"component_{id(controller_class)}"

    def get_fastapi_app(self) -> FastAPI:
        """
        Obtiene la instancia de FastAPI configurada.

        Returns:
            Instancia de FastAPI con todas las rutas configuradas
        """
        return self.fastapi_app
