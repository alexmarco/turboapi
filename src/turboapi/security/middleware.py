"""Middleware de seguridad para FastAPI."""

from collections.abc import Callable
from typing import Any

from fastapi import Request
from fastapi import Response
from starlette.middleware.base import BaseHTTPMiddleware

from .interfaces import BaseAuthProvider


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware de seguridad que añade headers de seguridad automáticamente.

    Este middleware se encarga de:
    - Añadir headers de seguridad estándar a todas las respuestas
    - Configurar CORS si es necesario
    - Proporcionar contexto de seguridad para la aplicación

    Parameters
    ----------
    auth_provider : BaseAuthProvider
        Proveedor de autenticación a usar en la aplicación.
    add_security_headers : bool, optional
        Si añadir headers de seguridad automáticamente (default: True).
    """

    def __init__(
        self,
        app: Any,
        auth_provider: BaseAuthProvider,
        add_security_headers: bool = True,
    ) -> None:
        """
        Inicializar el middleware de seguridad.

        Parameters
        ----------
        app
            Aplicación FastAPI.
        auth_provider : BaseAuthProvider
            Proveedor de autenticación.
        add_security_headers : bool, optional
            Si añadir headers de seguridad (default: True).
        """
        super().__init__(app)
        self.auth_provider = auth_provider
        self.add_security_headers = add_security_headers

    async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Response:
        """
        Procesar la request y añadir headers de seguridad a la respuesta.

        Parameters
        ----------
        request : Request
            Request entrante.
        call_next : Callable
            Siguiente middleware/handler en la cadena.

        Returns
        -------
        Response
            Respuesta con headers de seguridad añadidos.
        """
        # Procesar la request
        response = await call_next(request)

        # Add security headers if enabled
        if self.add_security_headers:
            self._add_security_headers(response)

        return response  # type: ignore[no-any-return]

    def _add_security_headers(self, response: Response) -> None:
        """
        Añadir headers de seguridad estándar a la respuesta.

        Parameters
        ----------
        response : Response
            Respuesta a la que añadir headers.
        """
        # Prevenir MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevenir carga en frames (clickjacking)
        response.headers["X-Frame-Options"] = "DENY"

        # Enable browser XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Force HTTPS in production (configurable)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Controlar referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Basic Content Security Policy
        response.headers["Content-Security-Policy"] = "default-src 'self'"


class CORSSecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware de CORS con configuración de seguridad.

    Proporciona configuración CORS segura con validación de orígenes.

    Parameters
    ----------
    allowed_origins : list[str]
        Lista de orígenes permitidos.
    allowed_methods : list[str], optional
        Métodos HTTP permitidos.
    allowed_headers : list[str], optional
        Headers permitidos.
    allow_credentials : bool, optional
        Si permitir credentials (default: False).
    """

    def __init__(
        self,
        app: Any,
        allowed_origins: list[str],
        allowed_methods: list[str] | None = None,
        allowed_headers: list[str] | None = None,
        allow_credentials: bool = False,
    ) -> None:
        """
        Inicializar el middleware de CORS.

        Parameters
        ----------
        app
            Aplicación FastAPI.
        allowed_origins : list[str]
            Orígenes permitidos.
        allowed_methods : list[str], optional
            Métodos permitidos.
        allowed_headers : list[str], optional
            Headers permitidos.
        allow_credentials : bool, optional
            Si permitir credentials.
        """
        super().__init__(app)
        self.allowed_origins = set(allowed_origins)
        self.allowed_methods = allowed_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allowed_headers = allowed_headers or [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
        ]
        self.allow_credentials = allow_credentials

    async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Response:
        """
        Procesar request CORS.

        Parameters
        ----------
        request : Request
            Request entrante.
        call_next : Callable
            Siguiente handler.

        Returns
        -------
        Response
            Respuesta con headers CORS.
        """
        origin = request.headers.get("origin")

        # Manejar preflight requests
        if request.method == "OPTIONS":
            response = Response()
        else:
            response = await call_next(request)

        # Add CORS headers if origin is allowed
        if origin and self._is_origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allowed_methods)
            response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allowed_headers)

            if self.allow_credentials:
                response.headers["Access-Control-Allow-Credentials"] = "true"

        return response

    def _is_origin_allowed(self, origin: str) -> bool:
        """
        Verificar si un origen está permitido.

        Parameters
        ----------
        origin : str
            Origen a verificar.

        Returns
        -------
        bool
            True si el origen está permitido.
        """
        # Permitir localhost en desarrollo
        if "localhost" in origin or "127.0.0.1" in origin:
            return True

        return origin in self.allowed_origins


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware básico de rate limiting.

    Implementa rate limiting simple basado en IP.

    Parameters
    ----------
    requests_per_minute : int
        Número máximo de requests por minuto por IP.
    """

    def __init__(
        self,
        app: Any,
        requests_per_minute: int = 60,
    ) -> None:
        """
        Inicializar el middleware de rate limiting.

        Parameters
        ----------
        app
            Aplicación FastAPI.
        requests_per_minute : int
            Requests permitidas por minuto.
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Response:
        """
        Aplicar rate limiting.

        Parameters
        ----------
        request : Request
            Request entrante.
        call_next : Callable
            Siguiente handler.

        Returns
        -------
        Response
            Respuesta o error 429 si excede el límite.
        """
        import time

        from fastapi import HTTPException
        from fastapi import status

        # Obtener IP del cliente
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()

        # Clean old requests (more than 1 minute)
        if client_ip in self.request_counts:
            self.request_counts[client_ip] = [
                req_time
                for req_time in self.request_counts[client_ip]
                if current_time - req_time < 60
            ]
        else:
            self.request_counts[client_ip] = []

        # Check limit
        if len(self.request_counts[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded"
            )

        # Registrar request actual
        self.request_counts[client_ip].append(current_time)

        return await call_next(request)  # type: ignore[no-any-return]


def setup_security_middleware(
    app: Any,
    auth_provider: BaseAuthProvider,
    cors_origins: list[str] | None = None,
    rate_limit_rpm: int = 60,
    enable_security_headers: bool = True,
) -> None:
    """
    Configurar todos los middlewares de seguridad en una aplicación FastAPI.

    Parameters
    ----------
    app
        Aplicación FastAPI.
    auth_provider : BaseAuthProvider
        Proveedor de autenticación.
    cors_origins : list[str], optional
        Orígenes CORS permitidos.
    rate_limit_rpm : int, optional
        Rate limit en requests por minuto (default: 60).
    enable_security_headers : bool, optional
        Si habilitar headers de seguridad (default: True).

    Examples
    --------
    >>> from fastapi import FastAPI
    >>> from turboapi.security.jwt import JWTAuthProvider
    >>>
    >>> app = FastAPI()
    >>> auth_provider = JWTAuthProvider(...)
    >>>
    >>> setup_security_middleware(
    ...     app,
    ...     auth_provider,
    ...     cors_origins=["http://localhost:3000"],
    ...     rate_limit_rpm=100
    ... )
    """
    # Add rate limiting middleware (first)
    if rate_limit_rpm > 0:
        app.add_middleware(RateLimitMiddleware, requests_per_minute=rate_limit_rpm)

    # Add CORS middleware if origins are specified
    if cors_origins:
        app.add_middleware(
            CORSSecurityMiddleware,
            allowed_origins=cors_origins,
            allow_credentials=True,
        )

    # Add main security middleware (last)
    app.add_middleware(
        SecurityMiddleware,
        auth_provider=auth_provider,
        add_security_headers=enable_security_headers,
    )
