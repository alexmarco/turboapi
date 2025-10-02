"""Interfaces del sistema de seguridad."""

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class AuthResult:
    """
    Resultado de una operación de autenticación.

    Parameters
    ----------
    success : bool
        Indica si la autenticación fue exitosa.
    user_id : str, optional
        ID del usuario autenticado.
    access_token : str, optional
        Token de acceso JWT.
    refresh_token : str, optional
        Token de renovación.
    expires_at : datetime, optional
        Fecha de expiración del token.
    error_message : str, optional
        Mensaje de error si la autenticación falló.
    """

    success: bool
    user_id: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    expires_at: datetime | None = None
    error_message: str | None = None


@dataclass
class TokenPayload:
    """
    Contenido (payload) de un token JWT.

    Parameters
    ----------
    user_id : str
        ID del usuario.
    username : str
        Nombre de usuario.
    roles : List[str]
        Lista de roles del usuario.
    permissions : List[str]
        Lista de permisos del usuario.
    issued_at : datetime
        Fecha de emisión del token.
    expires_at : datetime
        Fecha de expiración del token.
    extra_claims : Dict[str, Any]
        Claims adicionales en el token.
    """

    user_id: str
    username: str
    roles: list[str]
    permissions: list[str]
    issued_at: datetime
    expires_at: datetime
    extra_claims: dict[str, Any]


@dataclass
class User:
    """
    Representación de un usuario del sistema.

    Parameters
    ----------
    id : str
        Identificador único del usuario.
    username : str
        Nombre de usuario único.
    email : str
        Correo electrónico del usuario.
    is_active : bool
        Indica si el usuario está activo.
    is_verified : bool
        Indica si el email del usuario está verificado.
    roles : List[str]
        Lista de roles asignados al usuario.
    permissions : List[str]
        Lista de permisos del usuario.
    created_at : datetime
        Fecha de creación del usuario.
    last_login : datetime, optional
        Último inicio de sesión.
    extra_data : Dict[str, Any]
        Datos adicionales del usuario.
    """

    id: str
    username: str
    email: str
    is_active: bool
    is_verified: bool
    roles: list[str]
    permissions: list[str]
    created_at: datetime
    last_login: datetime | None = None
    extra_data: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Inicializar campos con valores por defecto."""
        if self.extra_data is None:
            self.extra_data = {}


@dataclass
class Role:
    """
    Representación de un rol del sistema.

    Parameters
    ----------
    name : str
        Nombre único del rol.
    description : str
        Descripción del rol.
    permissions : List[str]
        Lista de permisos incluidos en el rol.
    is_system_role : bool
        Indica si es un rol del sistema.
    created_at : datetime
        Fecha de creación del rol.
    """

    name: str
    description: str
    permissions: list[str]
    is_system_role: bool
    created_at: datetime


@dataclass
class Permission:
    """
    Representación de un permiso del sistema.

    Parameters
    ----------
    name : str
        Nombre único del permiso (ej: 'user:read').
    description : str
        Descripción del permiso.
    resource : str
        Recurso al que aplica el permiso.
    action : str
        Acción permitida sobre el recurso.
    created_at : datetime
        Fecha de creación del permiso.
    """

    name: str
    description: str
    resource: str
    action: str
    created_at: datetime


class BaseAuthProvider(ABC):
    """
    Interface base para proveedores de autenticación.

    Define los métodos que debe implementar cualquier proveedor
    de autenticación (JWT, OAuth2, etc.).
    """

    @abstractmethod
    async def authenticate(self, credentials: dict[str, Any]) -> AuthResult:
        """
        Autentica un usuario con las credenciales proporcionadas.

        Parameters
        ----------
        credentials : Dict[str, Any]
            Credenciales del usuario (username/password, token, etc.).

        Returns
        -------
        AuthResult
            Resultado de la autenticación.
        """
        ...

    @abstractmethod
    async def validate_token(self, token: str) -> TokenPayload:
        """
        Valida un token de acceso y extrae su payload.

        Parameters
        ----------
        token : str
            Token de acceso a validar.

        Returns
        -------
        TokenPayload
            Payload del token si es válido.

        Raises
        ------
        InvalidTokenError
            Si el token es inválido o ha expirado.
        """
        ...

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> AuthResult:
        """
        Renueva un token de acceso usando un refresh token.

        Parameters
        ----------
        refresh_token : str
            Token de renovación.

        Returns
        -------
        AuthResult
            Nuevo resultado de autenticación con tokens renovados.
        """
        ...

    @abstractmethod
    async def logout(self, token: str) -> bool:
        """
        Invalida un token (logout).

        Parameters
        ----------
        token : str
            Token a invalidar.

        Returns
        -------
        bool
            True si el logout fue exitoso.
        """
        ...

    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> User | None:
        """
        Obtiene un usuario por su ID.

        Parameters
        ----------
        user_id : str
            ID del usuario.

        Returns
        -------
        User, optional
            Usuario si existe, None si no se encuentra.
        """
        ...


class BaseTokenManager(ABC):
    """
    Interface base para la gestión de tokens JWT.

    Define los métodos para generar, verificar y revocar tokens.
    """

    @abstractmethod
    def generate_access_token(self, payload: dict[str, Any]) -> str:
        """
        Genera un token de acceso JWT.

        Parameters
        ----------
        payload : Dict[str, Any]
            Datos a incluir en el token.

        Returns
        -------
        str
            Token JWT generado.
        """
        ...

    @abstractmethod
    def generate_refresh_token(self, user_id: str) -> str:
        """
        Genera un token de renovación.

        Parameters
        ----------
        user_id : str
            ID del usuario.

        Returns
        -------
        str
            Token de renovación generado.
        """
        ...

    @abstractmethod
    def verify_access_token(self, token: str) -> TokenPayload:
        """
        Verifica y decodifica un token de acceso.

        Parameters
        ----------
        token : str
            Token a verificar.

        Returns
        -------
        TokenPayload
            Payload del token.

        Raises
        ------
        InvalidTokenError
            Si el token es inválido.
        """
        ...

    @abstractmethod
    def verify_refresh_token(self, token: str) -> str:
        """
        Verifica un token de renovación.

        Parameters
        ----------
        token : str
            Token de renovación.

        Returns
        -------
        str
            ID del usuario si el token es válido.

        Raises
        ------
        InvalidTokenError
            Si el token es inválido.
        """
        ...

    @abstractmethod
    async def revoke_token(self, token: str) -> bool:
        """
        Revoca un token (lo añade a una blacklist).

        Parameters
        ----------
        token : str
            Token a revocar.

        Returns
        -------
        bool
            True si la revocación fue exitosa.
        """
        ...


class BaseRBACManager(ABC):
    """
    Interface base para el Control de Acceso Basado en Roles (RBAC).

    Define los métodos para gestionar roles, permisos y verificar accesos.
    """

    @abstractmethod
    async def check_permission(self, user: User, resource: str, action: str) -> bool:
        """
        Verifica si un usuario tiene permiso para realizar una acción en un recurso.

        Parameters
        ----------
        user : User
            Usuario a verificar.
        resource : str
            Recurso al que se quiere acceder.
        action : str
            Acción que se quiere realizar.

        Returns
        -------
        bool
            True si el usuario tiene el permiso.
        """
        ...

    @abstractmethod
    async def check_role(self, user: User, role_name: str) -> bool:
        """
        Verifica si un usuario tiene un rol específico.

        Parameters
        ----------
        user : User
            Usuario a verificar.
        role_name : str
            Nombre del rol.

        Returns
        -------
        bool
            True si el usuario tiene el rol.
        """
        ...

    @abstractmethod
    async def assign_role(self, user_id: str, role_name: str) -> bool:
        """
        Asigna un rol a un usuario.

        Parameters
        ----------
        user_id : str
            ID del usuario.
        role_name : str
            Nombre del rol a asignar.

        Returns
        -------
        bool
            True si la asignación fue exitosa.
        """
        ...

    @abstractmethod
    async def revoke_role(self, user_id: str, role_name: str) -> bool:
        """
        Revoca un rol de un usuario.

        Parameters
        ----------
        user_id : str
            ID del usuario.
        role_name : str
            Nombre del rol a revocar.

        Returns
        -------
        bool
            True si la revocación fue exitosa.
        """
        ...

    @abstractmethod
    async def create_role(self, role: Role) -> bool:
        """
        Crea un nuevo rol en el sistema.

        Parameters
        ----------
        role : Role
            Rol a crear.

        Returns
        -------
        bool
            True si la creación fue exitosa.
        """
        ...

    @abstractmethod
    async def create_permission(self, permission: Permission) -> bool:
        """
        Crea un nuevo permiso en el sistema.

        Parameters
        ----------
        permission : Permission
            Permiso a crear.

        Returns
        -------
        bool
            True si la creación fue exitosa.
        """
        ...

    @abstractmethod
    async def get_user_roles(self, user_id: str) -> list[Role]:
        """
        Obtiene todos los roles de un usuario.

        Parameters
        ----------
        user_id : str
            ID del usuario.

        Returns
        -------
        List[Role]
            Lista de roles del usuario.
        """
        ...

    @abstractmethod
    async def get_user_permissions(self, user_id: str) -> list[Permission]:
        """
        Obtiene todos los permisos de un usuario (directos + de roles).

        Parameters
        ----------
        user_id : str
            ID del usuario.

        Returns
        -------
        List[Permission]
            Lista de permisos del usuario.
        """
        ...
