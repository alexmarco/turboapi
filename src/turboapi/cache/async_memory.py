"""Implementación de caché asíncrono en memoria."""

import asyncio
from datetime import timedelta
from typing import Any

from turboapi.interfaces import AsyncBaseCache
from turboapi.interfaces import CacheEntry


class AsyncInMemoryCache(AsyncBaseCache):
    """Implementación asíncrona en memoria de un sistema de caché."""

    def __init__(self) -> None:
        """Inicializa el caché asíncrono en memoria."""
        self._entries: dict[str, CacheEntry] = {}
        self._hits = 0
        self._misses = 0
        self._lock = asyncio.Lock()

    # Métodos asíncronos
    async def aget(self, key: str) -> Any:
        """
        Obtiene un valor del caché de forma asíncrona.

        Parameters
        ----------
        key : str
            Clave del valor.

        Returns
        -------
        Any
            El valor almacenado o None si no existe o ha expirado.

        Examples
        --------
        >>> cache = AsyncInMemoryCache()
        >>> await cache.aset("key", "value")
        >>> result = await cache.aget("key")
        >>> print(result)
        'value'
        """
        async with self._lock:
            entry = self._entries.get(key)

            if entry is None:
                self._misses += 1
                return None

            if entry.is_expired():
                # Eliminar entrada expirada
                del self._entries[key]
                self._misses += 1
                return None

            self._hits += 1
            return entry.access()

    async def aset(self, key: str, value: Any, ttl: timedelta | None = None) -> None:
        """
        Almacena un valor en el caché de forma asíncrona.

        Args:
            key: Clave del valor.
            value: Valor a almacenar.
            ttl: Tiempo de vida del valor.
        """
        async with self._lock:
            entry = CacheEntry(value=value, ttl=ttl)
            self._entries[key] = entry

    async def adelete(self, key: str) -> bool:
        """
        Elimina un valor del caché de forma asíncrona.

        Args:
            key: Clave del valor.

        Returns:
            True si se eliminó, False si no existía.
        """
        async with self._lock:
            if key in self._entries:
                del self._entries[key]
                return True
            return False

    async def aclear(self) -> None:
        """Limpia todo el caché de forma asíncrona."""
        async with self._lock:
            self._entries.clear()

    async def aexists(self, key: str) -> bool:
        """
        Verifica si una clave existe en el caché de forma asíncrona.

        Args:
            key: Clave a verificar.

        Returns:
            True si existe y no ha expirado, False en caso contrario.
        """
        async with self._lock:
            entry = self._entries.get(key)

            if entry is None:
                return False

            if entry.is_expired():
                # Eliminar entrada expirada
                del self._entries[key]
                return False

            return True

    async def akeys(self) -> list[str]:
        """
        Obtiene todas las claves del caché de forma asíncrona.

        Returns:
            Lista de claves válidas (no expiradas).
        """
        async with self._lock:
            valid_keys = []
            expired_keys = []

            for key, entry in self._entries.items():
                if entry.is_expired():
                    expired_keys.append(key)
                else:
                    valid_keys.append(key)

            # Limpiar entradas expiradas
            for key in expired_keys:
                del self._entries[key]

            return valid_keys

    async def asize(self) -> int:
        """
        Obtiene el número de entradas en el caché de forma asíncrona.

        Returns:
            Número de entradas válidas.
        """
        keys = await self.akeys()
        return len(keys)

    async def astats(self) -> dict[str, Any]:
        """
        Obtiene estadísticas del caché de forma asíncrona.

        Returns:
            Diccionario con estadísticas del caché.
        """
        async with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

            # Calcular entradas válidas sin llamar a akeys() para evitar deadlock
            valid_entries = 0
            expired_keys = []

            for key, entry in self._entries.items():
                if entry.is_expired():
                    expired_keys.append(key)
                else:
                    valid_entries += 1

            # Limpiar entradas expiradas
            for key in expired_keys:
                del self._entries[key]

            return {
                "total_entries": len(self._entries),
                "valid_entries": valid_entries,
                "hits": self._hits,
                "misses": self._misses,
                "total_requests": total_requests,
                "hit_rate": hit_rate,
            }
