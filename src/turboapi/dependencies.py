"""Dependencias y abstracciones de TurboAPI que ocultan FastAPI."""

from typing import Any
from typing import TypeVar

from fastapi import Depends as FastAPIDepends
from fastapi import HTTPException

from .security.dependencies import get_current_user as _get_current_user
from .security.dependencies import require_permission as _require_permission
from .security.dependencies import require_role as _require_role

T = TypeVar("T")


class TurboHTTPException(HTTPException):
    """Excepción HTTP de TurboAPI que encapsula FastAPI HTTPException."""

    pass


# Abstracciones para dependencias que ocultan FastAPI
def Depends(dependency: Any = None) -> Any:
    """
    Marca una función como dependencia de TurboAPI.

    Esta es una abstracción sobre FastAPI Depends que permite
    usar el sistema de DI de TurboAPI sin exponer FastAPI.

    Parameters
    ----------
    dependency : callable, optional
        Función o clase de dependencia.

    Returns
    -------
    Any
        Marcador de dependencia.

    Examples
    --------
    >>> from turboapi import TurboAPI
    >>> from turboapi.dependencies import Depends, get_current_user
    >>>
    >>> app = TurboAPI()
    >>>
    >>> @app.get("/profile")
    >>> async def get_profile(user: User = Depends(get_current_user)):
    ...     return {"username": user.username}
    """
    return FastAPIDepends(dependency)


# Directamente usar la función de dependencia sin wrapper
get_current_user = _get_current_user


def require_role(role: str) -> Any:
    """
    Crea una dependencia que requiere un rol específico.

    Parameters
    ----------
    role : str
        Rol requerido.

    Returns
    -------
    callable
        Función de dependencia.

    Examples
    --------
    >>> @app.get("/admin")
    >>> async def admin_panel(admin: User = Depends(require_role("admin"))):
    ...     return {"message": "admin access"}
    """
    return _require_role(role)


def require_permission(permission: str) -> Any:
    """
    Crea una dependencia que requiere un permiso específico.

    Parameters
    ----------
    permission : str
        Permiso requerido.

    Returns
    -------
    callable
        Función de dependencia.

    Examples
    --------
    >>> @app.delete("/users/{user_id}")
    >>> async def delete_user(
    ...     user_id: str,
    ...     admin: User = Depends(require_permission("user:delete"))
    ... ):
    ...     return {"deleted": user_id}
    """
    return _require_permission(permission)


# Funciones de utilidad para casos avanzados
def inject(name: str, expected_type: type[T] | None = None) -> T:
    """
    Inyecta un componente del contenedor DI de TurboAPI.

    Esta función permite acceder al sistema de DI de TurboAPI
    desde dentro de funciones de endpoint.

    Parameters
    ----------
    name : str
        Nombre del componente a inyectar.
    expected_type : Type[T], optional
        Tipo esperado del componente.

    Returns
    -------
    T
        Componente inyectado.

    Examples
    --------
    >>> @app.get("/data")
    >>> async def get_data():
    ...     db = inject("database", DatabaseService)
    ...     return await db.get_all()
    """
    # Esta función será implementada cuando tengamos acceso
    # al contexto de la aplicación TurboAPI
    raise NotImplementedError(
        "inject() function requires TurboAPI context. This will be implemented in future versions."
    )
