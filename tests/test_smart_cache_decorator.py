"""Pruebas para el decorador híbrido @SmartCache."""

import asyncio
from datetime import timedelta
from typing import Any

import pytest

from turboapi.cache.decorators import SmartCache


class TestSmartCacheDecorator:
    """Pruebas para el decorador híbrido @SmartCache."""

    def test_smart_cache_with_sync_function(self) -> None:
        """Prueba que @SmartCache detecta y maneja funciones síncronas."""
        call_count = 0

        @SmartCache()
        def sync_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        # Primera llamada - debe ejecutar la función
        result1 = sync_function(5)
        assert result1 == 10
        assert call_count == 1

        # Segunda llamada - debe usar caché
        result2 = sync_function(5)
        assert result2 == 10
        assert call_count == 1

        # Verificar metadatos
        assert hasattr(sync_function, "_is_smart_cached")
        assert sync_function._is_smart_cached is True
        assert hasattr(sync_function, "_cache_type")
        assert sync_function._cache_type == "sync"

    @pytest.mark.asyncio
    async def test_smart_cache_with_async_function(self) -> None:
        """Prueba que @SmartCache detecta y maneja funciones asíncronas."""
        call_count = 0

        @SmartCache()
        async def async_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.001)
            return x * 2

        # Primera llamada - debe ejecutar la función
        result1 = await async_function(5)
        assert result1 == 10
        assert call_count == 1

        # Segunda llamada - debe usar caché
        result2 = await async_function(5)
        assert result2 == 10
        assert call_count == 1

        # Verificar metadatos
        assert hasattr(async_function, "_is_smart_cached")
        assert async_function._is_smart_cached is True
        assert hasattr(async_function, "_cache_type")
        assert async_function._cache_type == "async"

    def test_smart_cache_sync_with_ttl(self) -> None:
        """Prueba @SmartCache con TTL en función síncrona."""
        call_count = 0

        @SmartCache(ttl=timedelta(milliseconds=10))
        def sync_function_with_ttl(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        # Primera llamada
        result1 = sync_function_with_ttl(5)
        assert result1 == 10
        assert call_count == 1

        # Segunda llamada inmediata - debe usar caché
        result2 = sync_function_with_ttl(5)
        assert result2 == 10
        assert call_count == 1

        # Esperar a que expire
        import time
        time.sleep(0.015)

        # Tercera llamada después de expirar
        result3 = sync_function_with_ttl(5)
        assert result3 == 10
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_smart_cache_async_with_ttl(self) -> None:
        """Prueba @SmartCache con TTL en función asíncrona."""
        call_count = 0

        @SmartCache(ttl=timedelta(milliseconds=10))
        async def async_function_with_ttl(x: int) -> int:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.001)
            return x * 2

        # Primera llamada
        result1 = await async_function_with_ttl(5)
        assert result1 == 10
        assert call_count == 1

        # Segunda llamada inmediata - debe usar caché
        result2 = await async_function_with_ttl(5)
        assert result2 == 10
        assert call_count == 1

        # Esperar a que expire
        await asyncio.sleep(0.015)

        # Tercera llamada después de expirar
        result3 = await async_function_with_ttl(5)
        assert result3 == 10
        assert call_count == 2

    def test_smart_cache_preserves_sync_metadata(self) -> None:
        """Prueba que @SmartCache preserva metadatos de funciones síncronas."""

        @SmartCache()
        def sync_function_with_metadata(x: int, y: str = "default") -> str:
            """A sync function with metadata."""
            return f"{x}-{y}"

        assert sync_function_with_metadata.__name__ == "sync_function_with_metadata"
        assert sync_function_with_metadata.__doc__ == "A sync function with metadata."

        result = sync_function_with_metadata(42, "test")
        assert result == "42-test"

    def test_smart_cache_preserves_async_metadata(self) -> None:
        """Prueba que @SmartCache preserva metadatos de funciones asíncronas."""

        @SmartCache()
        async def async_function_with_metadata(x: int, y: str = "default") -> str:
            """An async function with metadata."""
            await asyncio.sleep(0.001)
            return f"{x}-{y}"

        assert async_function_with_metadata.__name__ == "async_function_with_metadata"
        assert async_function_with_metadata.__doc__ == "An async function with metadata."

    def test_smart_cache_sync_clear_cache(self) -> None:
        """Prueba el método clear_cache en funciones síncronas."""
        call_count = 0

        @SmartCache()
        def sync_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        # Primera llamada
        result1 = sync_function(5)
        assert result1 == 10
        assert call_count == 1

        # Segunda llamada - usa caché
        result2 = sync_function(5)
        assert result2 == 10
        assert call_count == 1

        # Limpiar caché
        sync_function.clear_cache()  # type: ignore

        # Tercera llamada después de limpiar
        result3 = sync_function(5)
        assert result3 == 10
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_smart_cache_async_clear_cache(self) -> None:
        """Prueba el método aclear_cache en funciones asíncronas."""
        call_count = 0

        @SmartCache()
        async def async_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.001)
            return x * 2

        # Primera llamada
        result1 = await async_function(5)
        assert result1 == 10
        assert call_count == 1

        # Segunda llamada - usa caché
        result2 = await async_function(5)
        assert result2 == 10
        assert call_count == 1

        # Limpiar caché
        await async_function.aclear_cache()  # type: ignore

        # Tercera llamada después de limpiar
        result3 = await async_function(5)
        assert result3 == 10
        assert call_count == 2

    def test_smart_cache_mixed_usage(self) -> None:
        """Prueba que @SmartCache puede usarse en funciones sync y async simultáneamente."""
        sync_calls = 0
        async_calls = 0

        @SmartCache()
        def sync_func(x: int) -> str:
            nonlocal sync_calls
            sync_calls += 1
            return f"sync-{x}"

        @SmartCache()
        async def async_func(x: int) -> str:
            nonlocal async_calls
            async_calls += 1
            await asyncio.sleep(0.001)
            return f"async-{x}"

        # Usar función síncrona
        result1 = sync_func(1)
        assert result1 == "sync-1"
        assert sync_calls == 1

        result2 = sync_func(1)  # Debe usar caché
        assert result2 == "sync-1"
        assert sync_calls == 1

        # Usar función asíncrona
        async def test_async_part():
            nonlocal async_calls
            result3 = await async_func(1)
            assert result3 == "async-1"
            assert async_calls == 1

            result4 = await async_func(1)  # Debe usar caché
            assert result4 == "async-1"
            assert async_calls == 1

        # Ejecutar la parte asíncrona
        asyncio.run(test_async_part())

    def test_smart_cache_with_custom_key_function(self) -> None:
        """Prueba @SmartCache con función de clave personalizada."""
        call_count = 0

        @SmartCache(key_func=lambda x, y: f"custom_{x}_{y}")
        def sync_function_custom_key(x: int, y: int) -> int:
            nonlocal call_count
            call_count += 1
            return x + y

        result1 = sync_function_custom_key(1, 2)
        assert result1 == 3
        assert call_count == 1

        result2 = sync_function_custom_key(1, 2)
        assert result2 == 3
        assert call_count == 1  # Debe usar caché

        # Verificar metadatos
        assert hasattr(sync_function_custom_key, "_cache_key_func")

    def test_smart_cache_default_values(self) -> None:
        """Prueba los valores por defecto de @SmartCache."""

        @SmartCache()
        def sync_sample(x: int) -> int:
            return x * 2

        @SmartCache()
        async def async_sample(x: int) -> int:
            await asyncio.sleep(0.001)
            return x * 2

        # Verificar metadatos sync
        assert sync_sample._is_smart_cached is True
        assert sync_sample._cache_type == "sync"
        assert sync_sample._cache_ttl is None

        # Verificar metadatos async
        assert async_sample._is_smart_cached is True
        assert async_sample._cache_type == "async"
        assert async_sample._async_cache_ttl is None
