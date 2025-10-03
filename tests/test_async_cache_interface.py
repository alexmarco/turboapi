"""Pruebas para las interfaces de caché asíncrono."""

from abc import ABC

import pytest

from turboapi.interfaces import AsyncBaseCache


class TestAsyncBaseCache:
    """Pruebas para la interfaz AsyncBaseCache."""

    def test_async_base_cache_is_abstract(self) -> None:
        """Prueba que AsyncBaseCache es una clase abstracta."""
        assert issubclass(AsyncBaseCache, ABC)

        with pytest.raises(TypeError):
            AsyncBaseCache()  # type: ignore

    def test_async_base_cache_has_required_methods(self) -> None:
        """Prueba que AsyncBaseCache tiene los métodos requeridos."""
        # Verificar que los métodos abstractos están definidos
        abstract_methods = AsyncBaseCache.__abstractmethods__

        expected_methods = {
            "aget",
            "aset",
            "adelete",
            "aclear",
            "aexists",
            "akeys",
            "asize",
            "astats",
        }

        assert expected_methods.issubset(abstract_methods)

    def test_async_base_cache_method_signatures(self) -> None:
        """Prueba las firmas de los métodos de AsyncBaseCache."""
        # Esto se verificará cuando implementemos una clase concreta
        # Por ahora, solo verificamos que los métodos existen
        assert hasattr(AsyncBaseCache, "aget")
        assert hasattr(AsyncBaseCache, "aset")
        assert hasattr(AsyncBaseCache, "adelete")
        assert hasattr(AsyncBaseCache, "aclear")
        assert hasattr(AsyncBaseCache, "aexists")
        assert hasattr(AsyncBaseCache, "akeys")
        assert hasattr(AsyncBaseCache, "asize")
        assert hasattr(AsyncBaseCache, "astats")

    def test_async_base_cache_is_separate_from_base_cache(self) -> None:
        """Prueba que AsyncBaseCache es independiente de BaseCache."""
        from turboapi.interfaces import BaseCache

        # AsyncBaseCache NO debe heredar de BaseCache para evitar mezclar sync/async
        assert not issubclass(AsyncBaseCache, BaseCache)
        assert issubclass(AsyncBaseCache, ABC)

    def test_async_base_cache_has_only_async_methods(self) -> None:
        """Prueba que AsyncBaseCache solo tiene métodos asíncronos."""
        # AsyncBaseCache debe tener solo métodos async
        abstract_methods = AsyncBaseCache.__abstractmethods__

        async_methods = {
            "aget",
            "aset",
            "adelete",
            "aclear",
            "aexists",
            "akeys",
            "asize",
            "astats",
        }

        sync_methods = {
            "get",
            "set",
            "delete",
            "clear",
            "exists",
            "keys",
            "size",
            "stats",
        }

        # Debe tener solo métodos async
        assert async_methods.issubset(abstract_methods)
        # NO debe tener métodos sync
        assert not sync_methods.issubset(abstract_methods)
