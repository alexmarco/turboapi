class BaseCustomException(Exception):
    status_code: int = 500
    error_code: str = "INTERNAL_SERVER_ERROR"
    message_template: str = "An unexpected error occurred."

    def __init__(self, **kwargs: object) -> None:
        self.context = kwargs
        super().__init__(self.message_template.format(**self.context))

    def to_dict(self) -> dict[str, object]:
        return {
            "error": {
                "exception": self.error_code,
                "message": str(self),
                "context": self.context,
            },
            "status_code": self.status_code,
        }


class AuthenticationRequiredError(BaseCustomException):
    """
    Se lanza cuando se requiere autenticación para un recurso
    pero no se proporcionaron credenciales válidas.
    """

    status_code = 401
    error_code = "AUTHENTICATION_REQUIRED"
    message_template = "Authentication credentials were not provided or are invalid."


class PermissionDeniedError(BaseCustomException):
    """
    Se lanza cuando un usuario autenticado intenta acceder a un recurso
    para el cual no tiene los permisos necesarios.
    """

    status_code = 403
    error_code = "PERMISSION_DENIED"
    message_template = "You do not have permission to perform this action."


class DataAccessException(BaseCustomException):
    """
    Excepción base para errores relacionados con la capa de persistencia.
    """

    status_code = 500
    error_code = "DATA_ACCESS_ERROR"
    message_template = "A data access error occurred."


class DuplicateKeyException(DataAccessException):
    """
    Se lanza cuando ocurre una violación de clave única en la base de datos.
    """

    status_code = 409
    error_code = "DUPLICATE_KEY"
    message_template = "A record with the same unique key already exists."


class DataIntegrityViolationException(DataAccessException):
    """
    Se lanza cuando una operación viola la integridad de los datos.
    """

    status_code = 409
    error_code = "DATA_INTEGRITY_VIOLATION"
    message_template = "A data integrity violation occurred."


class ComponentRegistrationError(BaseCustomException):
    """Raised when a component cannot be registered in the DI container."""

    status_code = 500
    error_code = "COMPONENT_REGISTRATION_ERROR"
    message_template = "A component cannot be registered: {reason}"

    def __init__(self, *, reason: str) -> None:
        super().__init__(reason=reason)


class ConfigError(BaseCustomException):
    """Raised when there's an error loading or validating configuration."""

    status_code = 500
    error_code = "CONFIG_ERROR"
    message_template = "Configuration error: {reason}"

    def __init__(self, *, reason: str) -> None:
        super().__init__(reason=reason)
