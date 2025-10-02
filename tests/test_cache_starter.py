"""Pruebas para CacheStarter."""

from pathlib import Path

import pytest

from turboapi.cache.memory import InMemoryCache
from turboapi.cache.starter import CacheStarter
from turboapi.core.application import TurboApplication
from turboapi.core.config import TurboConfig
from turboapi.interfaces import BaseCache


def create_test_config() -> TurboConfig:
    """Crea una configuración de prueba."""
    return TurboConfig(
        project_name="test_project", project_version="1.0.0", installed_apps=["test_app"]
    )


def create_test_application() -> TurboApplication:
    """Crea una aplicación de prueba."""
    # Crear un archivo pyproject.toml temporal
    import tempfile

    pyproject_content = """[project]
name = "test_project"
version = "1.0.0"

[tool.turboapi]
installed_apps = ["test_app"]
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(pyproject_content)
        pyproject_path = Path(f.name)

    return TurboApplication(pyproject_path)


class TestCacheStarter:
    """Pruebas para CacheStarter."""

    def test_starter_initialization(self) -> None:
        """Prueba la inicialización del starter."""
        application = create_test_application()

        starter = CacheStarter(application)

        assert starter.application == application
        assert starter.cache_implementation == InMemoryCache

    def test_starter_initialization_with_custom_cache(self) -> None:
        """Prueba la inicialización del starter con caché personalizado."""
        application = create_test_application()

        class CustomCache(BaseCache):
            def get(self, key: str):
                return None

            def set(self, key: str, value, ttl=None):
                pass

            def delete(self, key: str):
                return False

            def clear(self):
                pass

            def exists(self, key: str):
                return False

            def keys(self):
                return []

            def size(self):
                return 0

            def stats(self):
                return {}

        starter = CacheStarter(application, cache_implementation=CustomCache)

        assert starter.cache_implementation == CustomCache

    def test_starter_configure(self) -> None:
        """Prueba la configuración del starter."""
        application = create_test_application()

        starter = CacheStarter(application)
        starter.configure()

        # Verificar que el caché se registró como singleton
        cache = application.container.resolve("cache")
        assert cache is not None
        assert isinstance(cache, InMemoryCache)

    def test_starter_configure_registers_singleton(self) -> None:
        """Prueba que el starter registra el caché como singleton."""
        application = create_test_application()

        starter = CacheStarter(application)
        starter.configure()

        # Obtener el caché dos veces debe devolver la misma instancia
        cache1 = application.container.resolve("cache")
        cache2 = application.container.resolve("cache")

        assert cache1 is cache2

    def test_starter_configure_with_custom_cache(self) -> None:
        """Prueba la configuración del starter con caché personalizado."""
        application = create_test_application()

        class CustomCache(BaseCache):
            def get(self, key: str):
                return None

            def set(self, key: str, value, ttl=None):
                pass

            def delete(self, key: str):
                return False

            def clear(self):
                pass

            def exists(self, key: str):
                return False

            def keys(self):
                return []

            def size(self):
                return 0

            def stats(self):
                return {}

        starter = CacheStarter(application, cache_implementation=CustomCache)
        starter.configure()

        # Verificar que se registró el caché personalizado
        cache = application.container.resolve("cache")
        assert cache is not None
        assert isinstance(cache, CustomCache)

    def test_starter_configure_idempotent(self) -> None:
        """Prueba que la configuración del starter es idempotente."""
        application = create_test_application()

        starter = CacheStarter(application)

        # Configurar múltiples veces
        starter.configure()
        cache1 = application.container.resolve("cache")

        starter.configure()
        cache2 = application.container.resolve("cache")

        # Debe ser la misma instancia
        assert cache1 is cache2

    def test_starter_get_cache(self) -> None:
        """Prueba obtener el caché del starter."""
        application = create_test_application()

        starter = CacheStarter(application)
        starter.configure()

        cache = starter.get_cache()
        assert cache is not None
        assert isinstance(cache, InMemoryCache)

    def test_starter_get_cache_before_configure(self) -> None:
        """Prueba obtener el caché antes de configurar."""
        application = create_test_application()

        starter = CacheStarter(application)

        with pytest.raises(RuntimeError, match="CacheStarter not configured"):
            starter.get_cache()

    def test_starter_is_configured(self) -> None:
        """Prueba el estado de configuración del starter."""
        application = create_test_application()

        starter = CacheStarter(application)

        assert not starter.is_configured()

        starter.configure()

        assert starter.is_configured()
