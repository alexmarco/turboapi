"""Starter para el sistema de caché."""

from turboapi.core.application import TurboApplication
from turboapi.core.di import ComponentProvider
from turboapi.interfaces import BaseCache

from .memory import InMemoryCache


class CacheStarter:
    """Starter para configurar el sistema de caché."""

    def __init__(
        self,
        application: TurboApplication,
        cache_implementation: type[BaseCache] = InMemoryCache,
    ) -> None:
        """
        Inicializa el starter de caché.

        Args:
            application: La aplicación TurboAPI.
            cache_implementation: Implementación del caché a usar.
        """
        self.application = application
        self.cache_implementation = cache_implementation
        self._configured = False

    def configure(self) -> None:
        """Configura el sistema de caché."""
        if self._configured:
            return

        # Registrar la implementación del caché como singleton
        self.application.container.register(
            "cache", ComponentProvider(lambda: self.cache_implementation(), singleton=True)
        )

        self._configured = True

    def get_cache(self) -> BaseCache:
        """
        Obtiene el caché configurado.

        Returns:
            La instancia del caché.

        Raises:
            RuntimeError: Si el starter no ha sido configurado.
        """
        if not self._configured:
            raise RuntimeError("CacheStarter not configured. Call configure() first.")

        cache = self.application.container.resolve("cache")
        if not isinstance(cache, BaseCache):
            raise TypeError(f"Expected BaseCache, got {type(cache)}")
        return cache

    def is_configured(self) -> bool:
        """
        Verifica si el starter ha sido configurado.

        Returns:
            True si está configurado, False en caso contrario.
        """
        return self._configured
