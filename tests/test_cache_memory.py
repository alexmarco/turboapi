"""Pruebas para las implementaciones de caché en memoria."""

import time
from datetime import timedelta

from turboapi.cache.memory import InMemoryCache
from turboapi.interfaces import BaseCache


class TestInMemoryCache:
    """Pruebas para InMemoryCache."""

    def test_cache_initialization(self) -> None:
        """Prueba la inicialización del caché."""
        cache = InMemoryCache()

        assert isinstance(cache, BaseCache)
        assert cache.size() == 0
        assert cache.keys() == []

    def test_cache_set_and_get(self) -> None:
        """Prueba almacenar y obtener valores del caché."""
        cache = InMemoryCache()

        # Almacenar un valor
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        assert cache.size() == 1

        # Almacenar otro valor
        cache.set("key2", {"data": "test"})
        assert cache.get("key2") == {"data": "test"}
        assert cache.size() == 2

    def test_cache_get_nonexistent_key(self) -> None:
        """Prueba obtener una clave que no existe."""
        cache = InMemoryCache()

        result = cache.get("nonexistent")
        assert result is None

    def test_cache_set_with_ttl(self) -> None:
        """Prueba almacenar valores con TTL."""
        cache = InMemoryCache()

        # Almacenar con TTL largo
        cache.set("key1", "value1", ttl=timedelta(seconds=10))
        assert cache.get("key1") == "value1"

        # Almacenar con TTL muy corto
        cache.set("key2", "value2", ttl=timedelta(milliseconds=1))
        time.sleep(0.002)  # Esperar a que expire
        assert cache.get("key2") is None

    def test_cache_exists(self) -> None:
        """Prueba verificar si una clave existe."""
        cache = InMemoryCache()

        assert not cache.exists("key1")

        cache.set("key1", "value1")
        assert cache.exists("key1")

        # Con TTL expirado
        cache.set("key2", "value2", ttl=timedelta(milliseconds=1))
        time.sleep(0.002)
        assert not cache.exists("key2")

    def test_cache_delete(self) -> None:
        """Prueba eliminar valores del caché."""
        cache = InMemoryCache()

        # Eliminar clave inexistente
        assert not cache.delete("nonexistent")

        # Eliminar clave existente
        cache.set("key1", "value1")
        assert cache.delete("key1")
        assert not cache.exists("key1")
        assert cache.size() == 0

    def test_cache_clear(self) -> None:
        """Prueba limpiar todo el caché."""
        cache = InMemoryCache()

        # Añadir varios valores
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        assert cache.size() == 3

        # Limpiar todo
        cache.clear()
        assert cache.size() == 0
        assert cache.keys() == []

    def test_cache_keys(self) -> None:
        """Prueba obtener todas las claves."""
        cache = InMemoryCache()

        # Caché vacío
        assert cache.keys() == []

        # Añadir claves
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        keys = cache.keys()
        assert len(keys) == 2
        assert "key1" in keys
        assert "key2" in keys

        # Con clave expirada
        cache.set("key3", "value3", ttl=timedelta(milliseconds=1))
        time.sleep(0.002)
        keys = cache.keys()
        assert len(keys) == 2
        assert "key3" not in keys

    def test_cache_size(self) -> None:
        """Prueba obtener el tamaño del caché."""
        cache = InMemoryCache()

        assert cache.size() == 0

        cache.set("key1", "value1")
        assert cache.size() == 1

        cache.set("key2", "value2")
        assert cache.size() == 2

        # Con clave expirada
        cache.set("key3", "value3", ttl=timedelta(milliseconds=1))
        time.sleep(0.002)
        assert cache.size() == 2  # No cuenta las expiradas

    def test_cache_stats(self) -> None:
        """Prueba obtener estadísticas del caché."""
        cache = InMemoryCache()

        stats = cache.stats()
        assert isinstance(stats, dict)
        assert "total_entries" in stats
        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate" in stats

        # Estadísticas iniciales
        assert stats["total_entries"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["hit_rate"] == 0.0

    def test_cache_hit_miss_statistics(self) -> None:
        """Prueba las estadísticas de hits y misses."""
        cache = InMemoryCache()

        # Miss inicial
        cache.get("nonexistent")
        stats = cache.stats()
        assert stats["misses"] == 1
        assert stats["hits"] == 0

        # Hit después de set
        cache.set("key1", "value1")
        cache.get("key1")
        stats = cache.stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5

    def test_cache_access_count(self) -> None:
        """Prueba que se actualiza el contador de accesos."""
        cache = InMemoryCache()

        cache.set("key1", "value1")

        # Primer acceso
        cache.get("key1")
        entry = cache._entries.get("key1")  # Acceso interno para testing
        assert entry is not None
        assert entry.access_count == 1

        # Segundo acceso
        cache.get("key1")
        assert entry.access_count == 2

    def test_cache_overwrite_value(self) -> None:
        """Prueba sobrescribir un valor existente."""
        cache = InMemoryCache()

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        cache.set("key1", "new_value")
        assert cache.get("key1") == "new_value"
        assert cache.size() == 1  # Sigue siendo una sola entrada

    def test_cache_with_different_types(self) -> None:
        """Prueba el caché con diferentes tipos de datos."""
        cache = InMemoryCache()

        # String
        cache.set("str", "hello")
        assert cache.get("str") == "hello"

        # Integer
        cache.set("int", 42)
        assert cache.get("int") == 42

        # List
        cache.set("list", [1, 2, 3])
        assert cache.get("list") == [1, 2, 3]

        # Dict
        cache.set("dict", {"a": 1, "b": 2})
        assert cache.get("dict") == {"a": 1, "b": 2}

        # None
        cache.set("none", None)
        assert cache.get("none") is None
        assert cache.exists("none")  # Debe existir aunque sea None
