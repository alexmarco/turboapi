"""Context managers para el sistema de caché asíncrono."""

import asyncio
from typing import Any

from ..interfaces import AsyncBaseCache
from .async_memory import AsyncInMemoryCache


class AsyncCacheContext:
    """
    Context manager para gestión automática del caché asíncrono.

    Proporciona un contexto donde se puede gestionar automáticamente
    el ciclo de vida del caché, incluyendo limpieza automática.
    """

    def __init__(
        self,
        cache_instance: AsyncBaseCache | None = None,
        auto_cleanup: bool = False,
    ) -> None:
        """
        Inicializa el contexto de caché asíncrono.

        Parameters
        ----------
        cache_instance : AsyncBaseCache, optional
            Instancia de caché a usar. Si no se proporciona, se crea una nueva.
        auto_cleanup : bool, default False
            Si True, limpia automáticamente el caché al salir del contexto.
        """
        self.cache_instance = cache_instance or AsyncInMemoryCache()
        self.auto_cleanup = auto_cleanup
        self._original_cache_instances: dict[str, Any] = {}

    async def __aenter__(self) -> "AsyncCacheContext":
        """
        Entra al contexto de caché asíncrono.

        Returns
        -------
        AsyncCacheContext
            La instancia del contexto.
        """
        # Aquí podríamos configurar el caché global si fuera necesario
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Sale del contexto de caché asíncrono.

        Parameters
        ----------
        exc_type : type, optional
            Tipo de excepción si ocurrió una.
        exc_val : Exception, optional
            Valor de la excepción si ocurrió una.
        exc_tb : traceback, optional
            Traceback de la excepción si ocurrió una.
        """
        if self.auto_cleanup:
            await self.cache_instance.aclear()

    async def get_stats(self) -> dict[str, Any]:
        """
        Obtiene estadísticas del caché en el contexto.

        Returns
        -------
        Dict[str, Any]
            Diccionario con estadísticas del caché.
        """
        return await self.cache_instance.astats()

    async def clear_cache(self) -> None:
        """
        Limpia el caché en el contexto.
        """
        await self.cache_instance.aclear()

    async def get_cache_size(self) -> int:
        """
        Obtiene el tamaño actual del caché.

        Returns
        -------
        int
            Número de entradas en el caché.
        """
        return await self.cache_instance.asize()

    async def cache_exists(self, key: str) -> bool:
        """
        Verifica si una clave existe en el caché.

        Parameters
        ----------
        key : str
            La clave a verificar.

        Returns
        -------
        bool
            True si la clave existe, False en caso contrario.
        """
        return await self.cache_instance.aexists(key)


class AsyncCacheManager:
    """
    Gestor global para instancias de caché asíncrono.

    Permite gestionar múltiples instancias de caché y coordinar
    su uso en diferentes contextos asyncio.
    """

    def __init__(self) -> None:
        """Inicializa el gestor de caché asíncrono."""
        self._caches: dict[str, AsyncBaseCache] = {}
        self._lock = asyncio.Lock()

    async def get_cache(self, name: str = "default") -> AsyncBaseCache:
        """
        Obtiene o crea una instancia de caché por nombre.

        Parameters
        ----------
        name : str, default "default"
            Nombre de la instancia de caché.

        Returns
        -------
        AsyncBaseCache
            La instancia de caché solicitada.
        """
        async with self._lock:
            if name not in self._caches:
                self._caches[name] = AsyncInMemoryCache()
            return self._caches[name]

    async def clear_cache(self, name: str = "default") -> None:
        """
        Limpia una instancia de caché específica.

        Parameters
        ----------
        name : str, default "default"
            Nombre de la instancia de caché a limpiar.
        """
        async with self._lock:
            if name in self._caches:
                await self._caches[name].aclear()

    async def clear_all_caches(self) -> None:
        """Limpia todas las instancias de caché."""
        async with self._lock:
            for cache in self._caches.values():
                await cache.aclear()

    async def get_all_stats(self) -> dict[str, dict[str, Any]]:
        """
        Obtiene estadísticas de todas las instancias de caché.

        Returns
        -------
        Dict[str, Dict[str, Any]]
            Diccionario con estadísticas de cada caché por nombre.
        """
        async with self._lock:
            stats = {}
            for name, cache in self._caches.items():
                stats[name] = await cache.astats()
            return stats

    async def remove_cache(self, name: str) -> None:
        """
        Remueve una instancia de caché.

        Parameters
        ----------
        name : str
            Nombre de la instancia de caché a remover.
        """
        async with self._lock:
            if name in self._caches:
                await self._caches[name].aclear()
                del self._caches[name]

    def list_caches(self) -> list[str]:
        """
        Lista los nombres de todas las instancias de caché.

        Returns
        -------
        list[str]
            Lista con los nombres de las instancias de caché.
        """
        return list(self._caches.keys())


# Instancia global del gestor de caché
_global_cache_manager = AsyncCacheManager()


async def get_global_cache(name: str = "default") -> AsyncBaseCache:
    """
    Obtiene una instancia de caché global.

    Parameters
    ----------
    name : str, default "default"
        Nombre de la instancia de caché.

    Returns
    -------
    AsyncBaseCache
        La instancia de caché solicitada.
    """
    return await _global_cache_manager.get_cache(name)


async def clear_global_cache(name: str = "default") -> None:
    """
    Limpia una instancia de caché global.

    Parameters
    ----------
    name : str, default "default"
        Nombre de la instancia de caché a limpiar.
    """
    await _global_cache_manager.clear_cache(name)


async def get_global_cache_stats() -> dict[str, dict[str, Any]]:
    """
    Obtiene estadísticas de todas las instancias de caché globales.

    Returns
    -------
    Dict[str, Dict[str, Any]]
        Diccionario con estadísticas de cada caché por nombre.
    """
    return await _global_cache_manager.get_all_stats()
