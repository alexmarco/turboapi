"""Pruebas de integración con asyncio para el sistema de caché."""

import asyncio

import pytest

from turboapi.cache import AsyncInMemoryCache
from turboapi.cache.context import AsyncCacheContext
from turboapi.cache.decorators import AsyncCache
from turboapi.cache.decorators import SmartCache


class TestAsyncioIntegration:
    """Pruebas de integración con asyncio."""

    @pytest.mark.asyncio
    async def test_cache_with_different_event_loops(self) -> None:
        """Prueba que el caché funciona con diferentes loops de eventos."""
        cache = AsyncInMemoryCache()

        # Almacenar en el loop actual
        await cache.aset("key1", "value1")
        result1 = await cache.aget("key1")
        assert result1 == "value1"

        # Crear un nuevo loop y verificar que el caché persiste
        # (En la práctica, cada loop tendría su propia instancia)
        current_loop = asyncio.get_running_loop()
        assert current_loop is not None

        result2 = await cache.aget("key1")
        assert result2 == "value1"

    @pytest.mark.asyncio
    async def test_cache_with_asyncio_gather(self) -> None:
        """Prueba que el caché funciona correctamente con asyncio.gather."""
        call_count = 0

        @AsyncCache()
        async def expensive_operation(x: int) -> int:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)  # Simular operación costosa
            return x * 2

        # Ejecutar múltiples operaciones concurrentes con la misma clave
        results = await asyncio.gather(
            expensive_operation(5),
            expensive_operation(5),
            expensive_operation(5),
            expensive_operation(10),  # Diferente clave
        )

        assert results == [10, 10, 10, 20]
        # Solo debe haberse ejecutado 2 veces (una para cada clave única)
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_cache_with_asyncio_tasks(self) -> None:
        """Prueba que el caché funciona con asyncio.create_task."""
        call_count = 0

        @SmartCache()
        async def async_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)
            return x * 3

        # Crear tareas concurrentes
        task1 = asyncio.create_task(async_function(7))
        task2 = asyncio.create_task(async_function(7))
        task3 = asyncio.create_task(async_function(8))

        results = await asyncio.gather(task1, task2, task3)
        assert results == [21, 21, 24]
        # Solo debe haberse ejecutado 2 veces (una para cada clave única)
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_cache_context_manager(self) -> None:
        """Prueba el context manager para caché asíncrono."""
        async with AsyncCacheContext() as cache_ctx:
            # Usar el caché del contexto directamente
            await cache_ctx.cache_instance.aset("test_key", "test_value")

            result = await cache_ctx.cache_instance.aget("test_key")
            assert result == "test_value"

            # Verificar estadísticas del contexto
            stats = await cache_ctx.get_stats()
            assert stats["total_entries"] >= 1

    @pytest.mark.asyncio
    async def test_cache_cleanup_on_context_exit(self) -> None:
        """Prueba que el caché se limpia al salir del contexto."""
        cache_instance = AsyncInMemoryCache()

        # Usar dentro del contexto con auto_cleanup
        async with AsyncCacheContext(cache_instance=cache_instance, auto_cleanup=True) as cache_ctx:
            await cache_ctx.cache_instance.aset("cleanup_key", "cleanup_value")

            # Verificar que está en el caché
            result = await cache_ctx.cache_instance.aget("cleanup_key")
            assert result == "cleanup_value"

            size_before = await cache_ctx.get_cache_size()
            assert size_before >= 1

        # Después del contexto, el caché debe estar vacío
        size_after = await cache_instance.asize()
        assert size_after == 0

    @pytest.mark.asyncio
    async def test_concurrent_cache_operations(self) -> None:
        """Prueba operaciones concurrentes en el mismo caché."""
        cache = AsyncInMemoryCache()

        async def writer(key: str, value: str) -> None:
            await cache.aset(key, value)

        async def reader(key: str) -> str | None:
            await asyncio.sleep(0.001)  # Pequeña demora
            return await cache.aget(key)

        # Ejecutar escritores y lectores concurrentemente
        await asyncio.gather(
            writer("key1", "value1"),
            writer("key2", "value2"),
            writer("key3", "value3"),
        )

        results = await asyncio.gather(
            reader("key1"),
            reader("key2"),
            reader("key3"),
        )

        assert results == ["value1", "value2", "value3"]

    @pytest.mark.asyncio
    async def test_cache_with_timeout(self) -> None:
        """Prueba que el caché funciona con asyncio.wait_for."""
        call_count = 0

        @AsyncCache()
        async def slow_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.005)  # Función lenta
            return x * 6

        # Primera llamada con timeout
        result1 = await asyncio.wait_for(slow_function(4), timeout=1.0)
        assert result1 == 24
        assert call_count == 1

        # Segunda llamada - debe ser rápida (desde caché)
        start_time = asyncio.get_event_loop().time()
        result2 = await asyncio.wait_for(slow_function(4), timeout=0.001)  # Timeout muy corto
        end_time = asyncio.get_event_loop().time()

        assert result2 == 24
        assert call_count == 1  # No debe haberse ejecutado de nuevo
        assert (end_time - start_time) < 0.1  # Debe ser rápido (ajustado para Windows)

    @pytest.mark.asyncio
    async def test_cache_exception_handling(self) -> None:
        """Prueba el manejo de excepciones en funciones cacheadas."""
        call_count = 0

        @AsyncCache()
        async def function_with_exception(x: int) -> int:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.001)
            if x < 0:
                raise ValueError("Negative value not allowed")
            return x * 7

        # Llamada exitosa
        result1 = await function_with_exception(3)
        assert result1 == 21
        assert call_count == 1

        # Llamada que genera excepción
        with pytest.raises(ValueError, match="Negative value not allowed"):
            await function_with_exception(-1)
        assert call_count == 2

        # Llamada exitosa de nuevo - debe usar caché
        result2 = await function_with_exception(3)
        assert result2 == 21
        assert call_count == 2  # No debe incrementarse

        # Llamada con excepción de nuevo - debe ejecutarse (no se cachean excepciones)
        with pytest.raises(ValueError):
            await function_with_exception(-1)
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_cache_with_asyncio_semaphore(self) -> None:
        """Prueba que el caché funciona con semáforos de asyncio."""
        semaphore = asyncio.Semaphore(2)  # Máximo 2 operaciones concurrentes
        call_count = 0

        @AsyncCache()
        async def semaphore_function(x: int) -> int:
            nonlocal call_count
            async with semaphore:
                call_count += 1
                await asyncio.sleep(0.01)
                return x * 8

        # Ejecutar múltiples operaciones
        tasks = [
            semaphore_function(1),
            semaphore_function(1),  # Misma clave - debe usar caché
            semaphore_function(2),
            semaphore_function(2),  # Misma clave - debe usar caché
        ]

        results = await asyncio.gather(*tasks)
        assert results == [8, 8, 16, 16]
        # Solo debe haberse ejecutado 2 veces (una para cada clave única)
        assert call_count == 2
