"""Pruebas para el descubrimiento de controladores en el escáner."""

from typing import Any
from unittest.mock import MagicMock

import pytest

from turboapi.core.discovery import ComponentScanner
from turboapi.web.decorators import Controller
from turboapi.web.decorators import Delete
from turboapi.web.decorators import Get
from turboapi.web.decorators import Post
from turboapi.web.decorators import Put


class TestControllerDiscovery:
    """Pruebas para el descubrimiento de controladores."""

    def test_find_controllers(self) -> None:
        """Prueba que se pueden encontrar controladores."""

        # Crear un módulo de prueba con controladores
        class TestModule:
            __name__ = "test_module"
            __file__ = "/path/to/test_module.py"

            @Controller(prefix="/api")
            class UserController:
                @Get("/users")
                def get_users(self) -> list[str]:
                    return ["user1", "user2"]

            @Controller(prefix="/api/v2")
            class ProductController:
                @Get("/products")
                def get_products(self) -> list[str]:
                    return ["product1", "product2"]

            class RegularClass:
                pass

        config = MagicMock()
        config.installed_apps = ["test_module"]

        scanner = ComponentScanner(config)

        with pytest.MonkeyPatch().context() as m:
            m.setattr("importlib.import_module", lambda name: TestModule)
            m.setattr("pathlib.Path", lambda path: MagicMock(glob=lambda pattern: []))

            controllers = scanner.find_controllers()

        # Verificar que encontró los controladores
        assert len(controllers) == 2
        assert TestModule.UserController in controllers
        assert TestModule.ProductController in controllers
        assert TestModule.RegularClass not in controllers

    def test_find_endpoints_in_controller(self) -> None:
        """Prueba que se pueden encontrar endpoints en un controlador."""

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

            def helper_method(self) -> str:
                return "helper"

        config = MagicMock()
        config.installed_apps = []

        scanner = ComponentScanner(config)
        endpoints = scanner.find_endpoints_in_controller(UserController)

        # Verificar que encontró todos los endpoints
        assert len(endpoints) == 4

        # Verificar que los endpoints están correctamente identificados
        http_methods = [endpoint[0] for endpoint in endpoints]
        paths = [endpoint[1] for endpoint in endpoints]
        functions = [endpoint[2] for endpoint in endpoints]

        assert "GET" in http_methods
        assert "POST" in http_methods
        assert "PUT" in http_methods
        assert "DELETE" in http_methods

        assert "/users" in paths
        assert "/users/{user_id}" in paths

        assert UserController.get_users in functions
        assert UserController.create_user in functions
        assert UserController.update_user in functions
        assert UserController.delete_user in functions
        assert UserController.helper_method not in functions

    def test_find_endpoints_with_controller_prefix(self) -> None:
        """Prueba que se respeta el prefijo del controlador."""

        @Controller(prefix="/api/v1")
        class UserController:
            @Get("/users")
            def get_users(self) -> list[str]:
                return ["user1", "user2"]

            @Get("/users/{user_id}")
            def get_user(self, user_id: int) -> str:
                return f"user {user_id}"

        config = MagicMock()
        config.installed_apps = []

        scanner = ComponentScanner(config)
        endpoints = scanner.find_endpoints_in_controller(UserController)

        # Verificar que se encontraron los endpoints
        assert len(endpoints) == 2

        # Verificar que las rutas no incluyen el prefijo (eso se manejará en el enrutamiento)
        paths = [endpoint[1] for endpoint in endpoints]
        assert "/users" in paths
        assert "/users/{user_id}" in paths

    def test_find_controllers_with_multiple_modules(self) -> None:
        """Prueba que se pueden encontrar controladores en múltiples módulos."""

        class Module1:
            __name__ = "module1"
            __file__ = "/path/to/module1.py"

            @Controller(prefix="/api")
            class UserController:
                @Get("/users")
                def get_users(self) -> list[str]:
                    return ["user1", "user2"]

        class Module2:
            __name__ = "module2"
            __file__ = "/path/to/module2.py"

            @Controller(prefix="/api/v2")
            class ProductController:
                @Get("/products")
                def get_products(self) -> list[str]:
                    return ["product1", "product2"]

        config = MagicMock()
        config.installed_apps = ["module1", "module2"]

        scanner = ComponentScanner(config)

        with pytest.MonkeyPatch().context() as m:

            def mock_import(name: str) -> Any:
                if name == "module1":
                    return Module1
                elif name == "module2":
                    return Module2
                else:
                    raise ImportError(f"No module named '{name}'")

            m.setattr("importlib.import_module", mock_import)
            m.setattr("pathlib.Path", lambda path: MagicMock(glob=lambda pattern: []))

            controllers = scanner.find_controllers()

        # Verificar que encontró controladores de ambos módulos
        assert len(controllers) == 2
        assert Module1.UserController in controllers
        assert Module2.ProductController in controllers

    def test_find_controllers_ignores_non_controllers(self) -> None:
        """Prueba que se ignoran las clases que no son controladores."""

        class TestModule:
            __name__ = "test_module"
            __file__ = "/path/to/test_module.py"

            class RegularClass:
                pass

            class ServiceClass:
                def __init__(self) -> None:
                    pass

            @Controller()
            class ControllerClass:
                @Get("/test")
                def test_endpoint(self) -> str:
                    return "test"

        config = MagicMock()
        config.installed_apps = ["test_module"]

        scanner = ComponentScanner(config)

        with pytest.MonkeyPatch().context() as m:
            m.setattr("importlib.import_module", lambda name: TestModule)
            m.setattr("pathlib.Path", lambda path: MagicMock(glob=lambda pattern: []))

            controllers = scanner.find_controllers()

        # Verificar que solo encontró el controlador
        assert len(controllers) == 1
        assert TestModule.ControllerClass in controllers
        assert TestModule.RegularClass not in controllers
        assert TestModule.ServiceClass not in controllers
