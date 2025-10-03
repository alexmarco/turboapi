"""Implementación de caché en memoria."""

from datetime import timedelta
from typing import Any

from turboapi.interfaces import BaseCache
from turboapi.interfaces import CacheEntry


class InMemoryCache(BaseCache):
    """Implementación en memoria de un sistema de caché."""

    def __init__(self) -> None:
        """Inicializa el caché en memoria."""
        self._entries: dict[str, CacheEntry] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Any:
        """
        Obtiene un valor del caché.

        Parameters
        ----------
        key : str
            Clave del valor.

        Returns
        -------
        Any or None
            El valor almacenado o None si no existe o ha expirado.
        """
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

    def set(self, key: str, value: Any, ttl: timedelta | None = None) -> None:
        """
        Almacena un valor en el caché.

        Args:
            key: Clave del valor.
            value: Valor a almacenar.
            ttl: Tiempo de vida del valor.
        """
        entry = CacheEntry(value=value, ttl=ttl)
        self._entries[key] = entry

    def delete(self, key: str) -> bool:
        """
        Elimina un valor del caché.

        Args:
            key: Clave del valor.

        Returns:
            True si se eliminó, False si no existía.
        """
        if key in self._entries:
            del self._entries[key]
            return True
        return False

    def clear(self) -> None:
        """Limpia todo el caché."""
        self._entries.clear()

    def exists(self, key: str) -> bool:
        """
        Verifica si una clave existe en el caché.

        Args:
            key: Clave a verificar.

        Returns:
            True si existe y no ha expirado, False en caso contrario.
        """
        entry = self._entries.get(key)

        if entry is None:
            return False

        if entry.is_expired():
            # Eliminar entrada expirada
            del self._entries[key]
            return False

        return True

    def keys(self) -> list[str]:
        """
        Obtiene todas las claves del caché.

        Returns:
            Lista de claves válidas (no expiradas).
        """
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

    def size(self) -> int:
        """
        Obtiene el número de entradas en el caché.

        Returns:
            Número de entradas válidas.
        """
        return len(self.keys())

    def stats(self) -> dict[str, Any]:
        """
        Obtiene estadísticas del caché.

        Returns:
            Diccionario con estadísticas del caché.
        """
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

        return {
            "total_entries": len(self._entries),
            "valid_entries": self.size(),
            "hits": self._hits,
            "misses": self._misses,
            "total_requests": total_requests,
            "hit_rate": hit_rate,
        }
