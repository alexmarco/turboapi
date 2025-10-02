"""Dependencias de FastAPI para seguridad."""

from typing import Callable
from fastapi import Depends, HTTPException, Request, status

from .exceptions import InvalidTokenError
from .interfaces import BaseAuthProvider, User


async def get_auth_provider() -> BaseAuthProvider:
    """
    Dependencia que obtiene el proveedor de autenticación.

    Esta dependencia debe ser sobrescrita en la aplicación real
    para proporcionar la instancia correcta del proveedor de autenticación.

    Returns
    -------
    BaseAuthProvider
        Instancia del proveedor de autenticación.

    Raises
    ------
    RuntimeError
        Si no se ha configurado un proveedor de autenticación.
    """
    raise RuntimeError(
        "Authentication provider not configured. "
        "Please configure the auth provider dependency in your FastAPI app."
    )


def _extract_token_from_header(authorization_header: str | None) -> str | None:
    """
    Extrae el token JWT del header Authorization.

    Parameters
    ----------
    authorization_header : str | None
        Valor del header Authorization.

    Returns
    -------
    str | None
        Token JWT si existe y está en formato válido, None si no.
    """
    if not authorization_header:
        return None
    
    # Verificar formato Bearer
    parts = authorization_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    return parts[1]


async def get_current_user_impl(
    request: Request,
    auth_provider: BaseAuthProvider
) -> User:
    """
    Implementación interna para obtener el usuario actual.

    Parameters
    ----------
    request : Request
        Request de FastAPI.
    auth_provider : BaseAuthProvider
        Proveedor de autenticación.

    Returns
    -------
    User
        Usuario autenticado.

    Raises
    ------
    HTTPException
        Si no hay token o el token es inválido.
    """
    # Extraer token del header Authorization
    authorization = request.headers.get("authorization")
    token = _extract_token_from_header(authorization)
    
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Validar token
        token_payload = await auth_provider.validate_token(token)
        
        # Obtener usuario completo
        user = await auth_provider.get_user_by_id(token_payload.user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    request: Request,
    auth_provider: BaseAuthProvider = Depends(get_auth_provider)
) -> User:
    """
    Dependencia de FastAPI para obtener el usuario actual autenticado.

    Esta dependencia extrae el token JWT del header Authorization,
    lo valida y retorna el usuario autenticado.

    Parameters
    ----------
    request : Request
        Request de FastAPI.
    auth_provider : BaseAuthProvider
        Proveedor de autenticación (inyectado).

    Returns
    -------
    User
        Usuario autenticado.

    Raises
    ------
    HTTPException
        401 si no hay token, es inválido, o el usuario no existe.

    Examples
    --------
    >>> @app.get("/profile")
    >>> async def get_profile(current_user: User = Depends(get_current_user)):
    ...     return {"username": current_user.username}
    """
    return await get_current_user_impl(request, auth_provider)


def require_role(required_role: str) -> Callable[[User], User]:
    """
    Crea una dependencia que requiere un rol específico.

    Parameters
    ----------
    required_role : str
        Rol requerido para acceder al endpoint.

    Returns
    -------
    Callable[[User], User]
        Dependencia que verifica el rol.

    Examples
    --------
    >>> @app.get("/admin")
    >>> async def admin_endpoint(admin: User = Depends(require_role("admin"))):
    ...     return {"message": "admin access"}
    """
    async def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        """
        Verifica que el usuario actual tenga el rol requerido.

        Parameters
        ----------
        current_user : User
            Usuario autenticado.

        Returns
        -------
        User
            Usuario si tiene el rol requerido.

        Raises
        ------
        HTTPException
            403 si el usuario no tiene el rol requerido.
        """
        if required_role not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        
        return current_user
    
    return role_dependency


def require_permission(required_permission: str) -> Callable[[User], User]:
    """
    Crea una dependencia que requiere un permiso específico.

    Parameters
    ----------
    required_permission : str
        Permiso requerido para acceder al endpoint.

    Returns
    -------
    Callable[[User], User]
        Dependencia que verifica el permiso.

    Examples
    --------
    >>> @app.delete("/users/{user_id}")
    >>> async def delete_user(
    ...     user_id: str,
    ...     admin: User = Depends(require_permission("user:delete"))
    ... ):
    ...     return {"message": f"User {user_id} deleted"}
    """
    async def permission_dependency(current_user: User = Depends(get_current_user)) -> User:
        """
        Verifica que el usuario actual tenga el permiso requerido.

        Parameters
        ----------
        current_user : User
            Usuario autenticado.

        Returns
        -------
        User
            Usuario si tiene el permiso requerido.

        Raises
        ------
        HTTPException
            403 si el usuario no tiene el permiso requerido.
        """
        if required_permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{required_permission}' required"
            )
        
        return current_user
    
    return permission_dependency


def require_roles(required_roles: list[str]) -> Callable[[User], User]:
    """
    Crea una dependencia que requiere uno de varios roles.

    Parameters
    ----------
    required_roles : list[str]
        Lista de roles válidos (usuario necesita al menos uno).

    Returns
    -------
    Callable[[User], User]
        Dependencia que verifica los roles.

    Examples
    --------
    >>> @app.get("/moderation")
    >>> async def mod_endpoint(
    ...     mod: User = Depends(require_roles(["admin", "moderator"]))
    ... ):
    ...     return {"message": "moderation access"}
    """
    async def roles_dependency(current_user: User = Depends(get_current_user)) -> User:
        """
        Verifica que el usuario actual tenga al menos uno de los roles requeridos.

        Parameters
        ----------
        current_user : User
            Usuario autenticado.

        Returns
        -------
        User
            Usuario si tiene al menos uno de los roles requeridos.

        Raises
        ------
        HTTPException
            403 si el usuario no tiene ninguno de los roles requeridos.
        """
        user_roles = set(current_user.roles)
        required_roles_set = set(required_roles)
        
        if not required_roles_set.intersection(user_roles):
            roles_str = ", ".join(required_roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these roles required: {roles_str}"
            )
        
        return current_user
    
    return roles_dependency


def require_permissions(required_permissions: list[str]) -> Callable[[User], User]:
    """
    Crea una dependencia que requiere múltiples permisos.

    Parameters
    ----------
    required_permissions : list[str]
        Lista de permisos requeridos (usuario necesita todos).

    Returns
    -------
    Callable[[User], User]
        Dependencia que verifica los permisos.

    Examples
    --------
    >>> @app.post("/admin/system")
    >>> async def system_action(
    ...     admin: User = Depends(require_permissions(["system:read", "system:write"]))
    ... ):
    ...     return {"message": "system action"}
    """
    async def permissions_dependency(current_user: User = Depends(get_current_user)) -> User:
        """
        Verifica que el usuario actual tenga todos los permisos requeridos.

        Parameters
        ----------
        current_user : User
            Usuario autenticado.

        Returns
        -------
        User
            Usuario si tiene todos los permisos requeridos.

        Raises
        ------
        HTTPException
            403 si el usuario no tiene alguno de los permisos requeridos.
        """
        user_permissions = set(current_user.permissions)
        required_permissions_set = set(required_permissions)
        
        if not required_permissions_set.issubset(user_permissions):
            missing = required_permissions_set - user_permissions
            missing_str = ", ".join(missing)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {missing_str}"
            )
        
        return current_user
    
    return permissions_dependency
