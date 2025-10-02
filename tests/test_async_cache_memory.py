"""Pruebas para las implementaciones de caché asíncrono en memoria."""

import asyncio
from datetime import timedelta

import pytest

from turboapi.cache.async_memory import AsyncInMemoryCache
from turboapi.interfaces import AsyncBaseCache


class TestAsyncInMemoryCache:
    """Pruebas para AsyncInMemoryCache."""

    def test_async_cache_initialization(self) -> None:
        """Prueba la inicialización del caché asíncrono."""
        cache = AsyncInMemoryCache()

        assert isinstance(cache, AsyncBaseCache)

    @pytest.mark.asyncio
    async def test_async_cache_set_and_get(self) -> None:
        """Prueba almacenar y obtener valores del caché de forma asíncrona."""
        cache = AsyncInMemoryCache()

        # Almacenar un valor
        await cache.aset("key1", "value1")
        result = await cache.aget("key1")
        assert result == "value1"

        size = await cache.asize()
        assert size == 1

        # Almacenar otro valor
        await cache.aset("key2", {"data": "test"})
        result = await cache.aget("key2")
        assert result == {"data": "test"}

        size = await cache.asize()
        assert size == 2

    @pytest.mark.asyncio
    async def test_async_cache_get_nonexistent_key(self) -> None:
        """Prueba obtener una clave que no existe de forma asíncrona."""
        cache = AsyncInMemoryCache()

        result = await cache.aget("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_async_cache_set_with_ttl(self) -> None:
        """Prueba almacenar valores con TTL de forma asíncrona."""
        cache = AsyncInMemoryCache()

        # Almacenar con TTL largo
        await cache.aset("key1", "value1", ttl=timedelta(seconds=10))
        result = await cache.aget("key1")
        assert result == "value1"

        # Almacenar con TTL muy corto
        await cache.aset("key2", "value2", ttl=timedelta(milliseconds=1))
        await asyncio.sleep(0.002)  # Esperar a que expire
        result = await cache.aget("key2")
        assert result is None

    @pytest.mark.asyncio
    async def test_async_cache_exists(self) -> None:
        """Prueba verificar si una clave existe de forma asíncrona."""
        cache = AsyncInMemoryCache()

        exists = await cache.aexists("key1")
        assert not exists

        await cache.aset("key1", "value1")
        exists = await cache.aexists("key1")
        assert exists

        # Con TTL expirado
        await cache.aset("key2", "value2", ttl=timedelta(milliseconds=1))
        await asyncio.sleep(0.002)
        exists = await cache.aexists("key2")
        assert not exists

    @pytest.mark.asyncio
    async def test_async_cache_delete(self) -> None:
        """Prueba eliminar valores del caché de forma asíncrona."""
        cache = AsyncInMemoryCache()

        # Eliminar clave inexistente
        deleted = await cache.adelete("nonexistent")
        assert not deleted

        # Eliminar clave existente
        await cache.aset("key1", "value1")
        deleted = await cache.adelete("key1")
        assert deleted

        exists = await cache.aexists("key1")
        assert not exists

        size = await cache.asize()
        assert size == 0

    @pytest.mark.asyncio
    async def test_async_cache_clear(self) -> None:
        """Prueba limpiar todo el caché de forma asíncrona."""
        cache = AsyncInMemoryCache()

        # Añadir varios valores
        await cache.aset("key1", "value1")
        await cache.aset("key2", "value2")
        await cache.aset("key3", "value3")

        size = await cache.asize()
        assert size == 3

        # Limpiar todo
        await cache.aclear()

        size = await cache.asize()
        assert size == 0

        keys = await cache.akeys()
        assert keys == []

    @pytest.mark.asyncio
    async def test_async_cache_keys(self) -> None:
        """Prueba obtener todas las claves de forma asíncrona."""
        cache = AsyncInMemoryCache()

        # Caché vacío
        keys = await cache.akeys()
        assert keys == []

        # Añadir claves
        await cache.aset("key1", "value1")
        await cache.aset("key2", "value2")

        keys = await cache.akeys()
        assert len(keys) == 2
        assert "key1" in keys
        assert "key2" in keys

        # Con clave expirada
        await cache.aset("key3", "value3", ttl=timedelta(milliseconds=1))
        await asyncio.sleep(0.002)

        keys = await cache.akeys()
        assert len(keys) == 2
        assert "key3" not in keys

    @pytest.mark.asyncio
    async def test_async_cache_size(self) -> None:
        """Prueba obtener el tamaño del caché de forma asíncrona."""
        cache = AsyncInMemoryCache()

        size = await cache.asize()
        assert size == 0

        await cache.aset("key1", "value1")
        size = await cache.asize()
        assert size == 1

        await cache.aset("key2", "value2")
        size = await cache.asize()
        assert size == 2

        # Con clave expirada
        await cache.aset("key3", "value3", ttl=timedelta(milliseconds=1))
        await asyncio.sleep(0.002)

        size = await cache.asize()
        assert size == 2  # No cuenta las expiradas

    @pytest.mark.asyncio
    async def test_async_cache_stats(self) -> None:
        """Prueba obtener estadísticas del caché de forma asíncrona."""
        cache = AsyncInMemoryCache()

        stats = await cache.astats()
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

    @pytest.mark.asyncio
    async def test_async_cache_hit_miss_statistics(self) -> None:
        """Prueba las estadísticas de hits y misses de forma asíncrona."""
        cache = AsyncInMemoryCache()

        # Miss inicial
        await cache.aget("nonexistent")
        stats = await cache.astats()
        assert stats["misses"] == 1
        assert stats["hits"] == 0

        # Hit después de set
        await cache.aset("key1", "value1")
        await cache.aget("key1")
        stats = await cache.astats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5

    @pytest.mark.asyncio
    async def test_async_cache_with_different_types(self) -> None:
        """Prueba el caché asíncrono con diferentes tipos de datos."""
        cache = AsyncInMemoryCache()

        # String
        await cache.aset("str", "hello")
        result = await cache.aget("str")
        assert result == "hello"

        # Integer
        await cache.aset("int", 42)
        result = await cache.aget("int")
        assert result == 42

        # List
        await cache.aset("list", [1, 2, 3])
        result = await cache.aget("list")
        assert result == [1, 2, 3]

        # Dict
        await cache.aset("dict", {"a": 1, "b": 2})
        result = await cache.aget("dict")
        assert result == {"a": 1, "b": 2}

        # None
        await cache.aset("none", None)
        result = await cache.aget("none")
        assert result is None

        exists = await cache.aexists("none")
        assert exists  # Debe existir aunque sea None

    @pytest.mark.asyncio
    async def test_async_cache_only(self) -> None:
        """Prueba que AsyncInMemoryCache es puramente asíncrono."""
        cache = AsyncInMemoryCache()

        # Solo métodos asíncronos disponibles
        await cache.aset("async_key", "async_value")
        result = await cache.aget("async_key")
        assert result == "async_value"

        # Verificar que no tiene métodos síncronos
        assert not hasattr(cache, "get")
        assert not hasattr(cache, "set")
        assert not hasattr(cache, "delete")
        assert not hasattr(cache, "clear")
        assert not hasattr(cache, "exists")
        assert not hasattr(cache, "keys")
        assert not hasattr(cache, "size")
        assert not hasattr(cache, "stats")

    @pytest.mark.asyncio
    async def test_concurrent_operations(self) -> None:
        """Prueba operaciones concurrentes en el caché asíncrono."""
        cache = AsyncInMemoryCache()

        # Operaciones concurrentes de escritura
        tasks = []
        for i in range(10):
            task = cache.aset(f"key_{i}", f"value_{i}")
            tasks.append(task)

        await asyncio.gather(*tasks)

        # Verificar que todas las claves se almacenaron
        size = await cache.asize()
        assert size == 10

        # Operaciones concurrentes de lectura
        read_tasks = []
        for i in range(10):
            task = cache.aget(f"key_{i}")
            read_tasks.append(task)

        results = await asyncio.gather(*read_tasks)

        # Verificar que todos los valores se leyeron correctamente
        for i, result in enumerate(results):
            assert result == f"value_{i}"
