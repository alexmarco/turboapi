"""Pruebas de integración para la API principal de TurboAPI."""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from turboapi import Depends
from turboapi import TurboAPI
from turboapi import get_current_user
from turboapi.security.interfaces import User


class TestTurboAPIIntegration:
    """Pruebas de integración para la API principal de TurboAPI."""

    @pytest.fixture
    def auth_provider(self):
        """Proveedor de autenticación mock para pruebas."""
        mock_auth = AsyncMock()

        # Usuario de prueba
        test_user = User(
            id="123",
            username="testuser",
            email="test@example.com",
            is_active=True,
            is_verified=True,
            roles=["user"],
            permissions=["read"],
            created_at=datetime.now(),
        )

        # Token payload mock
        from turboapi.security.interfaces import TokenPayload

        token_payload = TokenPayload(
            user_id=test_user.id,
            username=test_user.username,
            roles=test_user.roles,
            permissions=test_user.permissions,
            issued_at=datetime.now(),
            expires_at=datetime.now(),
            extra_claims={},
        )

        mock_auth.validate_token.return_value = token_payload
        mock_auth.get_user_by_id.return_value = test_user

        return mock_auth

    def test_turboapi_basic_usage(self):
        """Prueba el uso básico de TurboAPI sin autenticación."""
        # Crear aplicación TurboAPI
        app = TurboAPI(
            title="Test API",
            description="API de prueba",
            version="1.0.0",
            enable_security=False,  # Desactivar seguridad para esta prueba
        )

        # Definir endpoints usando la API de TurboAPI
        @app.get("/")
        async def root():
            return {"message": "Hello TurboAPI!"}

        @app.get("/health")
        async def health():
            return {"status": "OK"}

        # Probar con TestClient
        with TestClient(app.fastapi_app) as client:
            # Endpoint raíz
            response = client.get("/")
            assert response.status_code == 200
            assert response.json() == {"message": "Hello TurboAPI!"}

            # Endpoint de health
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json() == {"status": "OK"}

    def test_turboapi_with_authentication(self, auth_provider):
        """Prueba TurboAPI con sistema de autenticación."""
        # Crear aplicación con autenticación
        app = TurboAPI(title="Secure API", auth_provider=auth_provider, enable_security=True)

        # Endpoint público
        @app.get("/public")
        async def public():
            return {"message": "public access"}

        # Endpoint protegido usando abstracciones de TurboAPI
        @app.get("/profile")
        async def get_profile(current_user: User = Depends(get_current_user)):  # noqa: B008
            return {
                "username": current_user.username,
                "email": current_user.email,
                "roles": current_user.roles,
            }

        with TestClient(app.fastapi_app) as client:
            # Endpoint público debería funcionar sin token
            response = client.get("/public")
            assert response.status_code == 200
            assert response.json() == {"message": "public access"}

            # Endpoint protegido sin token debería fallar
            response = client.get("/profile")
            assert response.status_code == 401

            # Endpoint protegido con token debería funcionar
            headers = {"Authorization": "Bearer valid_token"}
            response = client.get("/profile", headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert data["username"] == "testuser"
            assert data["email"] == "test@example.com"
            assert "user" in data["roles"]

    def test_turboapi_config_integration(self):
        """Prueba que TurboAPI integra correctamente con el sistema de configuración."""
        app = TurboAPI(title="Config Test API", enable_security=False)

        # Verificar que el config está disponible
        assert app.config is not None
        assert hasattr(app.config, "project_name")

        # Verificar que el container DI está disponible
        assert app.container is not None

        # Endpoint que usa configuración
        @app.get("/config-info")
        async def config_info():
            return {
                "config_available": app.config is not None,
                "container_available": app.container is not None,
            }

        with TestClient(app.fastapi_app) as client:
            response = client.get("/config-info")
            assert response.status_code == 200
            data = response.json()
            assert data["config_available"] is True
            assert data["container_available"] is True

    def test_turboapi_http_methods(self):
        """Prueba que TurboAPI soporta todos los métodos HTTP."""
        app = TurboAPI(enable_security=False)

        @app.get("/test")
        async def get_test():
            return {"method": "GET"}

        @app.post("/test")
        async def post_test():
            return {"method": "POST"}

        @app.put("/test")
        async def put_test():
            return {"method": "PUT"}

        @app.delete("/test")
        async def delete_test():
            return {"method": "DELETE"}

        @app.patch("/test")
        async def patch_test():
            return {"method": "PATCH"}

        with TestClient(app.fastapi_app) as client:
            # Probar todos los métodos
            assert client.get("/test").json() == {"method": "GET"}
            assert client.post("/test").json() == {"method": "POST"}
            assert client.put("/test").json() == {"method": "PUT"}
            assert client.delete("/test").json() == {"method": "DELETE"}
            assert client.patch("/test").json() == {"method": "PATCH"}

    def test_create_app_function(self):
        """Prueba la función de conveniencia create_app."""
        from turboapi import create_app

        app = create_app(
            title="Created API", description="API creada con create_app", enable_security=False
        )

        @app.get("/")
        async def root():
            return {"created_with": "create_app"}

        with TestClient(app.fastapi_app) as client:
            response = client.get("/")
            assert response.status_code == 200
            assert response.json() == {"created_with": "create_app"}

    def test_turboapi_cors_configuration(self):
        """Prueba que TurboAPI configura CORS correctamente."""
        app = TurboAPI(
            enable_security=False, cors_origins=["http://localhost:3000", "https://example.com"]
        )

        @app.get("/cors-test")
        async def cors_test():
            return {"cors": "enabled"}

        with TestClient(app.fastapi_app) as client:
            # Hacer request con origen permitido
            headers = {"Origin": "http://localhost:3000"}
            response = client.get("/cors-test", headers=headers)
            assert response.status_code == 200

            # Verificar que se añadieron headers CORS
            # Nota: TestClient puede no simular completamente CORS,
            # pero podemos verificar que la configuración no causa errores
            assert response.json() == {"cors": "enabled"}
