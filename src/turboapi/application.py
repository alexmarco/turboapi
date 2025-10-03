"""Aplicación principal de TurboAPI."""

from collections.abc import Callable
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.application import TurboApplication
from .core.config import TurboConfig
from .security.dependencies import get_auth_provider
from .security.interfaces import BaseAuthProvider
from .security.middleware import setup_security_middleware


class TurboAPI:
    """
    Clase principal de TurboAPI que encapsula FastAPI y proporciona funcionalidades adicionales.

    Esta clase es la interfaz principal que los desarrolladores usarán en lugar de
    FastAPI directamente.
    Proporciona una API más limpia y potente con características adicionales como DI automática,
    configuración integrada, y sistema de seguridad.

    Parameters
    ----------
    title : str, optional
        Título de la aplicación (default: "TurboAPI Application").
    description : str, optional
        Descripción de la aplicación.
    version : str, optional
        Versión de la aplicación (default: "0.1.0").
    config_file : str, optional
        Archivo de configuración pyproject.toml (default: "pyproject.toml").
    installed_apps : List[str], optional
        Lista de aplicaciones instaladas para discovery automático.
    auth_provider : BaseAuthProvider, optional
        Proveedor de autenticación para el sistema de seguridad.
    enable_security : bool, optional
        Si habilitar el sistema de seguridad automáticamente (default: True).
    cors_origins : List[str], optional
        Orígenes CORS permitidos.

    Examples
    --------
    >>> from turboapi import TurboAPI
    >>> from turboapi.security import JWTAuthProvider
    >>>
    >>> app = TurboAPI(
    ...     title="Mi API",
    ...     installed_apps=["apps.users", "apps.products"],
    ...     auth_provider=JWTAuthProvider(...),
    ...     cors_origins=["http://localhost:3000"]
    ... )
    >>>
    >>> @app.get("/")
    >>> async def root():
    ...     return {"message": "Hello TurboAPI!"}
    """

    def __init__(
        self,
        title: str = "TurboAPI Application",
        description: str = "Built with TurboAPI framework",
        version: str = "0.1.0",
        config_file: str = "pyproject.toml",
        installed_apps: list[str] | None = None,
        auth_provider: BaseAuthProvider | None = None,
        enable_security: bool = True,
        cors_origins: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Inicializar la aplicación TurboAPI.

        Parameters
        ----------
        title : str, optional
            Título de la aplicación.
        description : str, optional
            Descripción de la aplicación.
        version : str, optional
            Versión de la aplicación.
        config_file : str, optional
            Archivo de configuración.
        installed_apps : List[str], optional
            Aplicaciones instaladas.
        auth_provider : BaseAuthProvider, optional
            Proveedor de autenticación.
        enable_security : bool, optional
            Si habilitar seguridad.
        cors_origins : List[str], optional
            Orígenes CORS.
        **kwargs
            Argumentos adicionales para FastAPI.
        """
        from pathlib import Path

        # Inicializar el core de TurboAPI
        pyproject_path = Path(config_file)
        self._turbo_app = TurboApplication(pyproject_path)

        # Configurar aplicaciones instaladas si se proporcionan
        if installed_apps:
            # Note: TurboConfig is immutable, this would need to be handled differently
            # For now, we'll skip this configuration
            pass

        # Inicializar el core (DI, discovery, etc.)
        self._turbo_app.initialize()

        # Crear la aplicación FastAPI subyacente
        self._fastapi_app = FastAPI(title=title, description=description, version=version, **kwargs)

        # Configurar el proveedor de autenticación
        self._auth_provider = auth_provider
        if auth_provider:
            self._setup_auth_provider_dependency()

        # Configurar middleware de seguridad
        if enable_security and auth_provider:
            self._setup_security_middleware(cors_origins)
        elif cors_origins:
            self._setup_cors_middleware(cors_origins)

    def _setup_auth_provider_dependency(self) -> None:
        """Configurar la dependencia del proveedor de autenticación."""

        def get_configured_auth_provider() -> BaseAuthProvider:
            if self._auth_provider is None:
                raise RuntimeError("Auth provider not configured")
            return self._auth_provider

        self._fastapi_app.dependency_overrides[get_auth_provider] = get_configured_auth_provider

    def _setup_security_middleware(self, cors_origins: list[str] | None) -> None:
        """Configurar middleware de seguridad."""
        if self._auth_provider is not None:
            setup_security_middleware(
                self._fastapi_app,
                self._auth_provider,
                cors_origins=cors_origins or [],
                rate_limit_rpm=60,  # Configurable en el futuro
                enable_security_headers=True,
            )

    def _setup_cors_middleware(self, cors_origins: list[str]) -> None:
        """Configurar middleware CORS básico."""
        self._fastapi_app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @property
    def fastapi_app(self) -> FastAPI:
        """
        Acceder a la aplicación FastAPI subyacente.

        Esto es útil para casos avanzados donde necesitas acceso directo a FastAPI,
        pero en general deberías usar la API de TurboAPI.

        Returns
        -------
        FastAPI
            La aplicación FastAPI subyacente.
        """
        return self._fastapi_app

    @property
    def config(self) -> TurboConfig:
        """
        Acceder a la configuración de la aplicación.

        Returns
        -------
        TurboConfig
            Configuración de la aplicación.
        """
        return self._turbo_app.config

    @property
    def container(self) -> Any:
        """
        Acceder al contenedor de inyección de dependencias.

        Returns
        -------
        TurboContainer
            Contenedor de DI.
        """
        return self._turbo_app.container

    def get(self, path: str, **kwargs: Any) -> Callable[..., Any]:
        """
        Decorador para endpoints GET.

        Parameters
        ----------
        path : str
            Ruta del endpoint.
        **kwargs
            Argumentos adicionales para FastAPI.

        Returns
        -------
        Callable
            Decorador de función.

        Examples
        --------
        >>> @app.get("/users")
        >>> async def list_users():
        ...     return {"users": []}
        """
        return self._fastapi_app.get(path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Callable[..., Any]:
        """
        Decorador para endpoints POST.

        Parameters
        ----------
        path : str
            Ruta del endpoint.
        **kwargs
            Argumentos adicionales para FastAPI.

        Returns
        -------
        Callable
            Decorador de función.
        """
        return self._fastapi_app.post(path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> Callable[..., Any]:
        """
        Decorador para endpoints PUT.

        Parameters
        ----------
        path : str
            Ruta del endpoint.
        **kwargs
            Argumentos adicionales para FastAPI.

        Returns
        -------
        Callable
            Decorador de función.
        """
        return self._fastapi_app.put(path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Callable[..., Any]:
        """
        Decorador para endpoints DELETE.

        Parameters
        ----------
        path : str
            Ruta del endpoint.
        **kwargs
            Argumentos adicionales para FastAPI.

        Returns
        -------
        Callable
            Decorador de función.
        """
        return self._fastapi_app.delete(path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> Callable[..., Any]:
        """
        Decorador para endpoints PATCH.

        Parameters
        ----------
        path : str
            Ruta del endpoint.
        **kwargs
            Argumentos adicionales para FastAPI.

        Returns
        -------
        Callable
            Decorador de función.
        """
        return self._fastapi_app.patch(path, **kwargs)

    def add_middleware(self, middleware_class: Any, **kwargs: Any) -> None:
        """
        Añadir middleware a la aplicación.

        Parameters
        ----------
        middleware_class
            Clase del middleware.
        **kwargs
            Argumentos del middleware.
        """
        self._fastapi_app.add_middleware(middleware_class, **kwargs)

    def include_router(self, router: Any, **kwargs: Any) -> None:
        """
        Incluir un router en la aplicación.

        Parameters
        ----------
        router
            Router a incluir.
        **kwargs
            Argumentos adicionales.
        """
        self._fastapi_app.include_router(router, **kwargs)

    def on_event(self, event_type: str) -> Callable[..., Any]:
        """
        Decorador para eventos de aplicación.

        Parameters
        ----------
        event_type : str
            Tipo de evento ("startup" o "shutdown").

        Returns
        -------
        Callable
            Decorador de función.

        Examples
        --------
        >>> @app.on_event("startup")
        >>> async def startup_event():
        ...     print("Application starting up...")
        """
        return self._fastapi_app.on_event(event_type)

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        """Permitir que TurboAPI sea llamado como una aplicación ASGI."""
        await self._fastapi_app(scope, receive, send)


# Función de conveniencia para crear aplicaciones
def create_app(title: str = "TurboAPI Application", **kwargs: Any) -> TurboAPI:
    """
    Función de conveniencia para crear una aplicación TurboAPI.

    Parameters
    ----------
    title : str, optional
        Título de la aplicación.
    **kwargs
        Argumentos adicionales para TurboAPI.

    Returns
    -------
    TurboAPI
        Nueva instancia de TurboAPI.

    Examples
    --------
    >>> from turboapi import create_app
    >>>
    >>> app = create_app(
    ...     title="Mi API",
    ...     installed_apps=["apps.users"]
    ... )
    """
    return TurboAPI(title=title, **kwargs)
