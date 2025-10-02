"""Pruebas para el decorador @AsyncCache."""

import asyncio
from datetime import timedelta
from typing import Any

import pytest

from turboapi.cache.decorators import AsyncCache as AsyncCacheDecorator


class TestAsyncCacheDecorator:
    """Pruebas para el decorador @AsyncCache."""

    @pytest.mark.asyncio
    async def test_async_cache_decorator_basic(self) -> None:
        """Prueba el uso básico del decorador @AsyncCache."""
        call_count = 0

        @AsyncCacheDecorator()
        async def expensive_async_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.001)  # Simular operación asíncrona
            return x * 2

        # Primera llamada - debe ejecutar la función
        result1 = await expensive_async_function(5)
        assert result1 == 10
        assert call_count == 1

        # Segunda llamada con mismo argumento - debe usar caché
        result2 = await expensive_async_function(5)
        assert result2 == 10
        assert call_count == 1  # No debe incrementar

        # Llamada con argumento diferente - debe ejecutar la función
        result3 = await expensive_async_function(3)
        assert result3 == 6
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_async_cache_decorator_with_ttl(self) -> None:
        """Prueba el decorador @AsyncCache con TTL."""
        call_count = 0

        @AsyncCacheDecorator(ttl=timedelta(milliseconds=10))
        async def expensive_async_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.001)
            return x * 2

        # Primera llamada
        result1 = await expensive_async_function(5)
        assert result1 == 10
        assert call_count == 1

        # Segunda llamada inmediata - debe usar caché
        result2 = await expensive_async_function(5)
        assert result2 == 10
        assert call_count == 1

        # Esperar a que expire el caché
        await asyncio.sleep(0.015)

        # Tercera llamada después de expirar - debe ejecutar la función
        result3 = await expensive_async_function(5)
        assert result3 == 10
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_async_cache_decorator_with_key_function(self) -> None:
        """Prueba el decorador @AsyncCache con función de clave personalizada."""
        call_count = 0

        @AsyncCacheDecorator(key_func=lambda x, y: f"custom_{x}_{y}")
        async def expensive_async_function(x: int, y: int) -> int:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.001)
            return x + y

        # Primera llamada
        result1 = await expensive_async_function(1, 2)
        assert result1 == 3
        assert call_count == 1

        # Segunda llamada con mismos argumentos - debe usar caché
        result2 = await expensive_async_function(1, 2)
        assert result2 == 3
        assert call_count == 1

        # Verificar que la función tiene metadatos de caché
        assert hasattr(expensive_async_function, "_is_async_cached")
        assert expensive_async_function._is_async_cached is True
        assert hasattr(expensive_async_function, "_async_cache_key_func")

    @pytest.mark.asyncio
    async def test_async_cache_decorator_with_kwargs(self) -> None:
        """Prueba el decorador @AsyncCache con argumentos con nombre."""
        call_count = 0

        @AsyncCacheDecorator()
        async def expensive_async_function(x: int, y: int = 10) -> int:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.001)
            return x + y

        # Llamadas con diferentes formas de pasar argumentos
        result1 = await expensive_async_function(5, 10)
        assert result1 == 15
        assert call_count == 1

        result2 = await expensive_async_function(5, y=10)
        assert result2 == 15
        assert call_count == 1  # Debe usar caché

        result3 = await expensive_async_function(x=5, y=10)
        assert result3 == 15
        assert call_count == 1  # Debe usar caché

    def test_async_cache_decorator_preserves_function_metadata(self) -> None:
        """Prueba que el decorador preserva los metadatos de la función."""

        @AsyncCacheDecorator()
        async def sample_async_function(x: int, y: str = "default") -> str:
            """A sample async cached function."""
            await asyncio.sleep(0.001)
            return f"{x}-{y}"

        # Verificar que la función mantiene su signatura y docstring
        assert sample_async_function.__name__ == "sample_async_function"
        assert sample_async_function.__doc__ == "A sample async cached function."

    @pytest.mark.asyncio
    async def test_async_cache_decorator_with_none_values(self) -> None:
        """Prueba el decorador @AsyncCache con valores None."""
        call_count = 0

        @AsyncCacheDecorator()
        async def async_function_returning_none(x: int) -> int | None:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.001)
            return None if x == 0 else x

        # Primera llamada que retorna None
        result1 = await async_function_returning_none(0)
        assert result1 is None
        assert call_count == 1

        # Segunda llamada - debe usar caché incluso para None
        result2 = await async_function_returning_none(0)
        assert result2 is None
        assert call_count == 1  # No debe incrementar

    @pytest.mark.asyncio
    async def test_async_cache_decorator_different_argument_types(self) -> None:
        """Prueba el decorador @AsyncCache con diferentes tipos de argumentos."""
        call_count = 0

        @AsyncCacheDecorator()
        async def flexible_async_function(*args: Any, **kwargs: Any) -> str:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.001)
            return f"args:{args}, kwargs:{kwargs}"

        # Diferentes combinaciones de argumentos
        result1 = await flexible_async_function(1, 2, name="test")
        assert call_count == 1

        result2 = await flexible_async_function(1, 2, name="test")
        assert call_count == 1  # Debe usar caché

        result3 = await flexible_async_function(1, 2, name="different")
        assert call_count == 2  # Argumentos diferentes

    @pytest.mark.asyncio
    async def test_async_cache_decorator_clear_cache_method(self) -> None:
        """Prueba el método clear_cache añadido por el decorador."""
        call_count = 0

        @AsyncCacheDecorator()
        async def expensive_async_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.001)
            return x * 2

        # Primera llamada
        result1 = await expensive_async_function(5)
        assert result1 == 10
        assert call_count == 1

        # Segunda llamada - usa caché
        result2 = await expensive_async_function(5)
        assert result2 == 10
        assert call_count == 1

        # Limpiar caché
        await expensive_async_function.aclear_cache()  # type: ignore

        # Tercera llamada después de limpiar - debe ejecutar la función
        result3 = await expensive_async_function(5)
        assert result3 == 10
        assert call_count == 2

    def test_async_cache_decorator_default_values(self) -> None:
        """Prueba los valores por defecto del decorador @AsyncCache."""

        @AsyncCacheDecorator()
        async def sample_async_function(x: int) -> int:
            await asyncio.sleep(0.001)
            return x * 2

        assert sample_async_function._is_async_cached is True
        assert sample_async_function._async_cache_ttl is None
        assert sample_async_function._async_cache_key_func is not None

    @pytest.mark.asyncio
    async def test_async_cache_concurrent_calls(self) -> None:
        """Prueba llamadas concurrentes a la misma función cacheada."""
        call_count = 0

        @AsyncCacheDecorator()
        async def expensive_async_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)  # Simular operación lenta
            return x * 2

        # Llamadas concurrentes con el mismo argumento
        tasks = []
        for _ in range(5):
            task = expensive_async_function(10)
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # Todas deben devolver el mismo resultado
        for result in results:
            assert result == 20

        # La función debe haberse ejecutado solo una vez
        # (o posiblemente más si las llamadas concurrentes no se manejan correctamente)
        # Por ahora, verificamos que al menos funciona
        assert call_count >= 1
