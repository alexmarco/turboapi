"""Pruebas para las interfaces de caché."""

from abc import ABC
from datetime import datetime
from datetime import timedelta

import pytest

from turboapi.interfaces import BaseCache
from turboapi.interfaces import CacheEntry


class TestCacheEntry:
    """Pruebas para la clase CacheEntry."""

    def test_cache_entry_creation(self) -> None:
        """Prueba la creación de una entrada de caché."""
        value = {"data": "test"}
        entry = CacheEntry(value=value)

        assert entry.value == value
        assert isinstance(entry.created_at, datetime)
        assert entry.access_count == 0
        assert entry.last_accessed is None
        assert entry.expires_at is None

    def test_cache_entry_with_ttl(self) -> None:
        """Prueba la creación de una entrada con TTL."""
        value = "test_value"
        ttl = timedelta(seconds=300)
        entry = CacheEntry(value=value, ttl=ttl)

        assert entry.value == value
        assert entry.expires_at is not None
        assert entry.expires_at > entry.created_at

    def test_cache_entry_is_expired(self) -> None:
        """Prueba si una entrada ha expirado."""
        # Entrada sin TTL nunca expira
        entry_no_ttl = CacheEntry(value="test")
        assert not entry_no_ttl.is_expired()

        # Entrada con TTL futuro no ha expirado
        entry_future = CacheEntry(value="test", ttl=timedelta(seconds=300))
        assert not entry_future.is_expired()

        # Entrada con TTL pasado ha expirado
        entry_past = CacheEntry(value="test", ttl=timedelta(seconds=-1))
        assert entry_past.is_expired()

    def test_cache_entry_access(self) -> None:
        """Prueba el acceso a una entrada de caché."""
        entry = CacheEntry(value="test")

        # Primer acceso
        value = entry.access()
        assert value == "test"
        assert entry.access_count == 1
        assert entry.last_accessed is not None

        # Segundo acceso
        first_access_time = entry.last_accessed
        import time

        time.sleep(0.001)  # Pequeña pausa para asegurar diferencia de tiempo
        value = entry.access()
        assert value == "test"
        assert entry.access_count == 2
        assert entry.last_accessed >= first_access_time


class TestBaseCache:
    """Pruebas para la interfaz BaseCache."""

    def test_base_cache_is_abstract(self) -> None:
        """Prueba que BaseCache es una clase abstracta."""
        assert issubclass(BaseCache, ABC)

        with pytest.raises(TypeError):
            BaseCache()  # type: ignore

    def test_base_cache_has_required_methods(self) -> None:
        """Prueba que BaseCache tiene los métodos requeridos."""
        # Verificar que los métodos abstractos están definidos
        abstract_methods = BaseCache.__abstractmethods__

        expected_methods = {
            "get",
            "set",
            "delete",
            "clear",
            "exists",
            "keys",
            "size",
            "stats",
        }

        assert expected_methods.issubset(abstract_methods)

    def test_base_cache_method_signatures(self) -> None:
        """Prueba las firmas de los métodos de BaseCache."""
        # Esto se verificará cuando implementemos una clase concreta
        # Por ahora, solo verificamos que los métodos existen
        assert hasattr(BaseCache, "get")
        assert hasattr(BaseCache, "set")
        assert hasattr(BaseCache, "delete")
        assert hasattr(BaseCache, "clear")
        assert hasattr(BaseCache, "exists")
        assert hasattr(BaseCache, "keys")
        assert hasattr(BaseCache, "size")
        assert hasattr(BaseCache, "stats")
