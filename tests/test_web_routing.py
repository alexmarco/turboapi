"""Pruebas para el sistema de enrutamiento web."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from turboapi.core.application import TurboApplication
from turboapi.web import Controller
from turboapi.web import Delete
from turboapi.web import Get
from turboapi.web import Post
from turboapi.web import Put
from turboapi.web import TurboAPI


class TestTurboAPI:
    """Pruebas para la clase TurboAPI."""

    def test_turboapi_initialization(self, tmp_path: Path) -> None:
        """Prueba que TurboAPI se inicializa correctamente."""
        # Crear pyproject.toml de prueba
        pyproject_content = """
[project]
name = "test_project"
version = "0.1.0"

[tool.turboapi]
installed_apps = []
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        app = TurboApplication(pyproject_file)
        turboapi = TurboAPI(app)

        assert turboapi.application is app
        assert turboapi.fastapi_app is not None
        assert turboapi.fastapi_app.title == "test_project"
        assert turboapi.fastapi_app.version == "0.1.0"

    def test_turboapi_with_controller(self, tmp_path: Path) -> None:
        """Prueba que TurboAPI registra correctamente un controlador."""

        # Crear un controlador de prueba
        class TestModule:
            __name__ = "test_module"
            __file__ = "/path/to/test_module.py"

            @Controller(prefix="/api")
            class UserController:
                def __init__(self) -> None:
                    self.users = ["user1", "user2"]

                @Get("/users")
                def get_users(self) -> list[str]:
                    return self.users

                @Post("/users")
                def create_user(self) -> str:
                    return "created"

        # Crear pyproject.toml de prueba
        pyproject_content = """
[project]
name = "test_project"
version = "0.1.0"

[tool.turboapi]
installed_apps = ["test_module"]
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        app = TurboApplication(pyproject_file)

        # Mock el importlib para devolver nuestro módulo de prueba
        with pytest.MonkeyPatch().context() as m:
            m.setattr("importlib.import_module", lambda name: TestModule)
            m.setattr("pathlib.Path", lambda path: MagicMock(glob=lambda pattern: []))

            turboapi = TurboAPI(app)

        # Verificar que se creó la aplicación FastAPI
        assert turboapi.fastapi_app is not None

        # Usar TestClient para probar los endpoints
        client = TestClient(turboapi.fastapi_app)

        # Probar el endpoint GET
        response = client.get("/api/users")
        assert response.status_code == 200
        assert response.json() == ["user1", "user2"]

        # Probar el endpoint POST
        response = client.post("/api/users")
        assert response.status_code == 201
        assert response.json() == "created"

    def test_turboapi_with_multiple_controllers(self, tmp_path: Path) -> None:
        """Prueba que TurboAPI registra múltiples controladores."""

        # Crear múltiples controladores de prueba
        class TestModule:
            __name__ = "test_module"
            __file__ = "/path/to/test_module.py"

            @Controller(prefix="/api/users")
            class UserController:
                def __init__(self) -> None:
                    pass

                @Get("/")
                def get_users(self) -> list[str]:
                    return ["user1", "user2"]

                @Get("/{user_id}")
                def get_user(self, user_id: int) -> str:
                    return f"user {user_id}"

            @Controller(prefix="/api/products")
            class ProductController:
                def __init__(self) -> None:
                    pass

                @Get("/")
                def get_products(self) -> list[str]:
                    return ["product1", "product2"]

                @Post("/")
                def create_product(self) -> str:
                    return "product created"

        # Crear pyproject.toml de prueba
        pyproject_content = """
[project]
name = "test_project"
version = "0.1.0"

[tool.turboapi]
installed_apps = ["test_module"]
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        app = TurboApplication(pyproject_file)

        # Mock el importlib para devolver nuestro módulo de prueba
        with pytest.MonkeyPatch().context() as m:
            m.setattr("importlib.import_module", lambda name: TestModule)
            m.setattr("pathlib.Path", lambda path: MagicMock(glob=lambda pattern: []))

            turboapi = TurboAPI(app)

        # Usar TestClient para probar los endpoints
        client = TestClient(turboapi.fastapi_app)

        # Probar endpoints de usuarios
        response = client.get("/api/users/")
        assert response.status_code == 200
        assert response.json() == ["user1", "user2"]

        response = client.get("/api/users/1")
        assert response.status_code == 200
        assert response.json() == "user 1"

        # Probar endpoints de productos
        response = client.get("/api/products/")
        assert response.status_code == 200
        assert response.json() == ["product1", "product2"]

        response = client.post("/api/products/")
        assert response.status_code == 201
        assert response.json() == "product created"

    def test_turboapi_with_controller_metadata(self, tmp_path: Path) -> None:
        """Prueba que TurboAPI respeta los metadatos de los controladores."""

        # Crear un controlador con metadatos
        class TestModule:
            __name__ = "test_module"
            __file__ = "/path/to/test_module.py"

            @Controller(prefix="/api", tags=["users"])
            class UserController:
                def __init__(self) -> None:
                    pass

                @Get(
                    "/users",
                    tags=["api"],
                    summary="Get all users",
                    description="Retrieve all users from the system",
                )
                def get_users(self) -> list[str]:
                    return ["user1", "user2"]

        # Crear pyproject.toml de prueba
        pyproject_content = """
[project]
name = "test_project"
version = "0.1.0"

[tool.turboapi]
installed_apps = ["test_module"]
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        app = TurboApplication(pyproject_file)

        # Mock el importlib para devolver nuestro módulo de prueba
        with pytest.MonkeyPatch().context() as m:
            m.setattr("importlib.import_module", lambda name: TestModule)
            m.setattr("pathlib.Path", lambda path: MagicMock(glob=lambda pattern: []))

            turboapi = TurboAPI(app)

        # Verificar que se creó la aplicación FastAPI
        assert turboapi.fastapi_app is not None

        # Usar TestClient para probar el endpoint
        client = TestClient(turboapi.fastapi_app)

        response = client.get("/api/users")
        assert response.status_code == 200
        assert response.json() == ["user1", "user2"]

    def test_turboapi_with_different_http_methods(self, tmp_path: Path) -> None:
        """Prueba que TurboAPI maneja diferentes métodos HTTP."""

        # Crear un controlador con diferentes métodos HTTP
        class TestModule:
            __name__ = "test_module"
            __file__ = "/path/to/test_module.py"

            @Controller(prefix="/api")
            class CRUDController:
                def __init__(self) -> None:
                    pass

                @Get("/items")
                def get_items(self) -> list[str]:
                    return ["item1", "item2"]

                @Post("/items")
                def create_item(self) -> str:
                    return "item created"

                @Put("/items/{item_id}")
                def update_item(self, item_id: int) -> str:
                    return f"item {item_id} updated"

                @Delete("/items/{item_id}")
                def delete_item(self, item_id: int) -> str:
                    return f"item {item_id} deleted"

        # Crear pyproject.toml de prueba
        pyproject_content = """
[project]
name = "test_project"
version = "0.1.0"

[tool.turboapi]
installed_apps = ["test_module"]
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        app = TurboApplication(pyproject_file)

        # Mock el importlib para devolver nuestro módulo de prueba
        with pytest.MonkeyPatch().context() as m:
            m.setattr("importlib.import_module", lambda name: TestModule)
            m.setattr("pathlib.Path", lambda path: MagicMock(glob=lambda pattern: []))

            turboapi = TurboAPI(app)

        # Usar TestClient para probar los diferentes métodos HTTP
        client = TestClient(turboapi.fastapi_app)

        # GET
        response = client.get("/api/items")
        assert response.status_code == 200
        assert response.json() == ["item1", "item2"]

        # POST
        response = client.post("/api/items")
        assert response.status_code == 201
        assert response.json() == "item created"

        # PUT
        response = client.put("/api/items/1")
        assert response.status_code == 200
        assert response.json() == "item 1 updated"

        # DELETE
        response = client.delete("/api/items/1")
        assert response.status_code == 204
        # DELETE con status 204 no devuelve contenido

    def test_get_fastapi_app(self, tmp_path: Path) -> None:
        """Prueba que get_fastapi_app devuelve la aplicación FastAPI."""
        # Crear pyproject.toml de prueba
        pyproject_content = """
[project]
name = "test_project"
version = "0.1.0"

[tool.turboapi]
installed_apps = []
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        app = TurboApplication(pyproject_file)
        turboapi = TurboAPI(app)

        fastapi_app = turboapi.get_fastapi_app()

        assert fastapi_app is turboapi.fastapi_app
        assert fastapi_app.title == "test_project"
        assert fastapi_app.version == "0.1.0"
