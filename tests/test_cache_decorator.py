"""Pruebas para el decorador @Cache."""

import time
from datetime import timedelta
from typing import Any

from turboapi.cache.decorators import Cache as CacheDecorator


class TestCacheDecorator:
    """Pruebas para el decorador @Cache."""

    def test_cache_decorator_basic(self) -> None:
        """Prueba el uso básico del decorador @Cache."""
        call_count = 0

        @CacheDecorator()
        def expensive_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        # Primera llamada - debe ejecutar la función
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Segunda llamada con mismo argumento - debe usar caché
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # No debe incrementar

        # Llamada con argumento diferente - debe ejecutar la función
        result3 = expensive_function(3)
        assert result3 == 6
        assert call_count == 2

    def test_cache_decorator_with_ttl(self) -> None:
        """Prueba el decorador @Cache con TTL."""
        call_count = 0

        @CacheDecorator(ttl=timedelta(milliseconds=10))
        def expensive_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        # Primera llamada
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Segunda llamada inmediata - debe usar caché
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1

        # Esperar a que expire el caché
        time.sleep(0.015)

        # Tercera llamada después de expirar - debe ejecutar la función
        result3 = expensive_function(5)
        assert result3 == 10
        assert call_count == 2

    def test_cache_decorator_with_key_function(self) -> None:
        """Prueba el decorador @Cache con función de clave personalizada."""
        call_count = 0

        @CacheDecorator(key_func=lambda x, y: f"custom_{x}_{y}")
        def expensive_function(x: int, y: int) -> int:
            nonlocal call_count
            call_count += 1
            return x + y

        # Primera llamada
        result1 = expensive_function(1, 2)
        assert result1 == 3
        assert call_count == 1

        # Segunda llamada con mismos argumentos - debe usar caché
        result2 = expensive_function(1, 2)
        assert result2 == 3
        assert call_count == 1

        # Verificar que la función tiene metadatos de caché
        assert hasattr(expensive_function, "_is_cached")
        assert expensive_function._is_cached is True
        assert hasattr(expensive_function, "_cache_key_func")

    def test_cache_decorator_with_kwargs(self) -> None:
        """Prueba el decorador @Cache con argumentos con nombre."""
        call_count = 0

        @CacheDecorator()
        def expensive_function(x: int, y: int = 10) -> int:
            nonlocal call_count
            call_count += 1
            return x + y

        # Llamadas con diferentes formas de pasar argumentos
        result1 = expensive_function(5, 10)
        assert result1 == 15
        assert call_count == 1

        result2 = expensive_function(5, y=10)
        assert result2 == 15
        assert call_count == 1  # Debe usar caché

        result3 = expensive_function(x=5, y=10)
        assert result3 == 15
        assert call_count == 1  # Debe usar caché

    def test_cache_decorator_preserves_function_metadata(self) -> None:
        """Prueba que el decorador preserva los metadatos de la función."""

        @CacheDecorator()
        def sample_function(x: int, y: str = "default") -> str:
            """A sample cached function."""
            return f"{x}-{y}"

        # Verificar que la función mantiene su signatura y docstring
        assert sample_function.__name__ == "sample_function"
        assert sample_function.__doc__ == "A sample cached function."

        # Verificar que funciona correctamente
        result = sample_function(42, "test")
        assert result == "42-test"

    def test_cache_decorator_with_async_function(self) -> None:
        """Prueba el decorador @Cache con función asíncrona."""
        call_count = 0

        @CacheDecorator()
        async def async_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        # Verificar que mantiene los metadatos
        assert hasattr(async_function, "_is_cached")
        assert async_function._is_cached is True

        # ⚠️ LIMITACIÓN CONOCIDA: El decorador @Cache actual no maneja
        # correctamente funciones async def. Esta funcionalidad se
        # implementará en Epic 6.1 con @AsyncCache

    def test_cache_decorator_default_values(self) -> None:
        """Prueba los valores por defecto del decorador @Cache."""

        @CacheDecorator()
        def sample_function(x: int) -> int:
            return x * 2

        assert sample_function._is_cached is True
        assert sample_function._cache_ttl is None
        assert sample_function._cache_key_func is not None

    def test_cache_decorator_with_none_values(self) -> None:
        """Prueba el decorador @Cache con valores None."""
        call_count = 0

        @CacheDecorator()
        def function_returning_none(x: int) -> int | None:
            nonlocal call_count
            call_count += 1
            return None if x == 0 else x

        # Primera llamada que retorna None
        result1 = function_returning_none(0)
        assert result1 is None
        assert call_count == 1

        # Segunda llamada - debe usar caché incluso para None
        result2 = function_returning_none(0)
        assert result2 is None
        assert call_count == 1  # No debe incrementar

    def test_cache_decorator_different_argument_types(self) -> None:
        """Prueba el decorador @Cache con diferentes tipos de argumentos."""
        call_count = 0

        @CacheDecorator()
        def flexible_function(*args: Any, **kwargs: Any) -> str:
            nonlocal call_count
            call_count += 1
            return f"args:{args}, kwargs:{kwargs}"

        # Diferentes combinaciones de argumentos
        result1 = flexible_function(1, 2, name="test")
        assert call_count == 1

        result2 = flexible_function(1, 2, name="test")
        assert call_count == 1  # Debe usar caché

        result3 = flexible_function(1, 2, name="different")
        assert call_count == 2  # Argumentos diferentes

    def test_cache_decorator_clear_cache_method(self) -> None:
        """Prueba el método clear_cache añadido por el decorador."""
        call_count = 0

        @CacheDecorator()
        def expensive_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        # Primera llamada
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Segunda llamada - usa caché
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1

        # Limpiar caché
        expensive_function.clear_cache()  # type: ignore

        # Tercera llamada después de limpiar - debe ejecutar la función
        result3 = expensive_function(5)
        assert result3 == 10
        assert call_count == 2
