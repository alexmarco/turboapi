"""Excepciones del sistema de seguridad."""


class SecurityError(Exception):
    """Excepción base para errores de seguridad."""

    pass


class InvalidTokenError(SecurityError):
    """
    Excepción lanzada cuando un token es inválido o ha expirado.

    Parameters
    ----------
    message : str
        Mensaje descriptivo del error.
    """

    def __init__(self, message: str = "Invalid or expired token") -> None:
        super().__init__(message)
        self.message = message


class AuthenticationError(SecurityError):
    """
    Excepción lanzada cuando falla la autenticación.

    Parameters
    ----------
    message : str
        Mensaje descriptivo del error.
    """

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message)
        self.message = message


class AuthorizationError(SecurityError):
    """
    Excepción lanzada cuando un usuario no tiene permisos suficientes.

    Parameters
    ----------
    message : str
        Mensaje descriptivo del error.
    """

    def __init__(self, message: str = "Access denied") -> None:
        super().__init__(message)
        self.message = message


class UserNotFoundError(SecurityError):
    """
    Excepción lanzada cuando un usuario no existe.

    Parameters
    ----------
    message : str
        Mensaje descriptivo del error.
    """

    def __init__(self, message: str = "User not found") -> None:
        super().__init__(message)
        self.message = message


class UserInactiveError(SecurityError):
    """
    Excepción lanzada cuando un usuario está inactivo.

    Parameters
    ----------
    message : str
        Mensaje descriptivo del error.
    """

    def __init__(self, message: str = "User is inactive") -> None:
        super().__init__(message)
        self.message = message
