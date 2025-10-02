"""Pruebas para los decoradores de la capa web."""

from turboapi.web.decorators import Controller
from turboapi.web.decorators import Delete
from turboapi.web.decorators import Get
from turboapi.web.decorators import Post
from turboapi.web.decorators import Put
from turboapi.web.utils import get_controller_metadata


class TestControllerDecorator:
    """Pruebas para el decorador @Controller."""

    def test_controller_decorator_basic(self) -> None:
        """Prueba que el decorador @Controller marca correctamente una clase."""

        @Controller()
        class TestController:
            pass

        metadata = get_controller_metadata(TestController)
        assert metadata["is_controller"] is True
        assert metadata["prefix"] == ""
        assert metadata["tags"] == []
        assert metadata["dependencies"] == []

    def test_controller_decorator_with_prefix(self) -> None:
        """Prueba que el decorador @Controller acepta un prefijo."""

        @Controller(prefix="/api/v1")
        class TestController:
            pass

        assert TestController._controller_prefix  # type: ignore == "/api/v1"

    def test_controller_decorator_with_tags(self) -> None:
        """Prueba que el decorador @Controller acepta etiquetas."""

        @Controller(tags=["users", "api"])
        class TestController:
            pass

        assert TestController._controller_tags  # type: ignore == ["users", "api"]

    def test_controller_decorator_with_dependencies(self) -> None:
        """Prueba que el decorador @Controller acepta dependencias."""
        dep1 = object()
        dep2 = object()

        @Controller(dependencies=[dep1, dep2])
        class TestController:
            pass

        assert TestController._controller_dependencies  # type: ignore == [dep1, dep2]


class TestGetDecorator:
    """Pruebas para el decorador @Get."""

    def test_get_decorator_basic(self) -> None:
        """Prueba que el decorador @Get marca correctamente un método."""

        @Get()
        def test_endpoint() -> str:
            return "test"

        assert hasattr(test_endpoint, "_is_endpoint")
        assert test_endpoint._is_endpoint is True  # type: ignore
        assert test_endpoint._http_method == "GET"  # type: ignore
        assert test_endpoint._endpoint_path == ""  # type: ignore
        assert test_endpoint._status_code == 200  # type: ignore

    def test_get_decorator_with_path(self) -> None:
        """Prueba que el decorador @Get acepta una ruta."""

        @Get("/users")
        def test_endpoint() -> str:
            return "test"

        assert test_endpoint._endpoint_path  # type: ignore == "/users"

    def test_get_decorator_with_custom_status_code(self) -> None:
        """Prueba que el decorador @Get acepta un código de estado personalizado."""

        @Get(status_code=201)
        def test_endpoint() -> str:
            return "test"

        assert test_endpoint._status_code  # type: ignore == 201

    def test_get_decorator_with_metadata(self) -> None:
        """Prueba que el decorador @Get acepta metadatos."""

        @Get(path="/users", tags=["users"], summary="Get users", description="Retrieve all users")
        def test_endpoint() -> str:
            return "test"

        assert test_endpoint._endpoint_path  # type: ignore == "/users"
        assert test_endpoint._endpoint_tags  # type: ignore == ["users"]
        assert test_endpoint._endpoint_summary  # type: ignore == "Get users"
        assert test_endpoint._endpoint_description  # type: ignore == "Retrieve all users"


class TestPostDecorator:
    """Pruebas para el decorador @Post."""

    def test_post_decorator_basic(self) -> None:
        """Prueba que el decorador @Post marca correctamente un método."""

        @Post()
        def test_endpoint() -> str:
            return "test"

        assert test_endpoint._is_endpoint  # type: ignore is True
        assert test_endpoint._http_method  # type: ignore == "POST"
        assert test_endpoint._status_code  # type: ignore == 201

    def test_post_decorator_with_custom_status_code(self) -> None:
        """Prueba que el decorador @Post acepta un código de estado personalizado."""

        @Post(status_code=200)
        def test_endpoint() -> str:
            return "test"

        assert test_endpoint._status_code  # type: ignore == 200


class TestPutDecorator:
    """Pruebas para el decorador @Put."""

    def test_put_decorator_basic(self) -> None:
        """Prueba que el decorador @Put marca correctamente un método."""

        @Put()
        def test_endpoint() -> str:
            return "test"

        assert test_endpoint._is_endpoint  # type: ignore is True
        assert test_endpoint._http_method  # type: ignore == "PUT"
        assert test_endpoint._status_code  # type: ignore == 200


class TestDeleteDecorator:
    """Pruebas para el decorador @Delete."""

    def test_delete_decorator_basic(self) -> None:
        """Prueba que el decorador @Delete marca correctamente un método."""

        @Delete()
        def test_endpoint() -> str:
            return "test"

        assert test_endpoint._is_endpoint  # type: ignore is True
        assert test_endpoint._http_method  # type: ignore == "DELETE"
        assert test_endpoint._status_code  # type: ignore == 204


class TestControllerWithEndpoints:
    """Pruebas para controladores con endpoints."""

    def test_controller_with_endpoints(self) -> None:
        """Prueba que un controlador puede tener múltiples endpoints."""

        @Controller(prefix="/api")
        class UserController:
            @Get("/users")
            def get_users(self) -> list[str]:
                return ["user1", "user2"]

            @Post("/users")
            def create_user(self) -> str:
                return "created"

            @Put("/users/{user_id}")
            def update_user(self, user_id: int) -> str:
                return f"updated {user_id}"

            @Delete("/users/{user_id}")
            def delete_user(self, user_id: int) -> str:
                return f"deleted {user_id}"

        # Verificar que la clase es un controlador
        assert UserController._is_controller  # type: ignore is True
        assert UserController._controller_prefix  # type: ignore == "/api"

        # Verificar que los métodos son endpoints
        assert UserController.get_users._is_endpoint  # type: ignore is True
        assert UserController.get_users._http_method  # type: ignore == "GET"
        assert UserController.get_users._endpoint_path  # type: ignore == "/users"

        assert UserController.create_user._is_endpoint  # type: ignore is True
        assert UserController.create_user._http_method  # type: ignore == "POST"
        assert UserController.create_user._endpoint_path  # type: ignore == "/users"

        assert UserController.update_user._is_endpoint  # type: ignore is True
        assert UserController.update_user._http_method  # type: ignore == "PUT"
        assert UserController.update_user._endpoint_path  # type: ignore == "/users/{user_id}"

        assert UserController.delete_user._is_endpoint  # type: ignore is True
        assert UserController.delete_user._http_method  # type: ignore == "DELETE"
        assert UserController.delete_user._endpoint_path  # type: ignore == "/users/{user_id}"
