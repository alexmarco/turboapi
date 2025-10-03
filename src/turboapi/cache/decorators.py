"""Decoradores para el sistema de caché."""

import asyncio
import functools
import hashlib
import inspect
import json
from collections.abc import Callable
from datetime import timedelta
from typing import Any
from typing import TypeVar

from .memory import InMemoryCache

F = TypeVar("F", bound=Callable[..., Any])


class BaseCacheDecorator:
    """
    Clase base para decoradores de caché.

    Proporciona funcionalidad común para generar claves de caché
    y normalizar argumentos.
    """

    def __init__(
        self,
        ttl: timedelta | None = None,
        key_func: Callable[..., str] | None = None,
    ) -> None:
        """
        Inicializa el decorador base de caché.

        Parameters
        ----------
        ttl : timedelta, optional
            Tiempo de vida del caché.
        key_func : Callable, optional
            Función personalizada para generar claves de caché.
        """
        self.ttl = ttl
        self.key_func = key_func or self._default_key_func

    def _default_key_func(self, *args: Any, **kwargs: Any) -> str:
        """
        Genera una clave de caché por defecto basada en argumentos.

        Parameters
        ----------
        *args : Any
            Argumentos posicionales.
        **kwargs : Any
            Argumentos con nombre.

        Returns
        -------
        str
            Clave de caché como string.
        """
        # Crear una representación determinística de los argumentos
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items()) if kwargs else {},
        }

        # Serializar a JSON y crear hash
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()

    def _normalize_arguments(
        self, func: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> tuple[tuple[Any, ...], dict[str, Any]]:
        """
        Normaliza argumentos para generar claves consistentes.

        Parameters
        ----------
        func : Callable
            La función original.
        args : tuple
            Argumentos posicionales.
        kwargs : dict
            Argumentos con nombre.

        Returns
        -------
        tuple
            Tupla con argumentos normalizados.
        """
        try:
            # Obtener la signatura de la función
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Convertir a argumentos posicionales y con nombre normalizados
            normalized_kwargs = dict(bound_args.arguments)
            return (), normalized_kwargs
        except Exception:
            # Si falla la normalización, usar argumentos originales
            return args, kwargs

    def _generate_cache_key(
        self, func: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> str:
        """
        Genera una clave de caché para la función y argumentos dados.

        Parameters
        ----------
        func : Callable
            La función original.
        args : tuple
            Argumentos posicionales.
        kwargs : dict
            Argumentos con nombre.

        Returns
        -------
        str
            Clave de caché generada.
        """
        # Normalizar argumentos para generar clave consistente
        normalized_args, normalized_kwargs = self._normalize_arguments(func, args, kwargs)

        # Generar clave de caché
        return f"{func.__name__}:{self.key_func(*normalized_args, **normalized_kwargs)}"


class Cache(BaseCacheDecorator):
    """
    Decorador para añadir caché automático a funciones síncronas.

    Para funciones asíncronas, usar @AsyncCache.
    Para detección automática, usar @SmartCache.
    """

    def __init__(
        self,
        ttl: timedelta | None = None,
        key_func: Callable[..., str] | None = None,
        cache_instance: Any = None,
    ) -> None:
        """
        Inicializa el decorador de caché.

        Parameters
        ----------
        ttl : timedelta, optional
            Tiempo de vida del caché.
        key_func : Callable, optional
            Función personalizada para generar claves de caché.
        cache_instance : Any, optional
            Instancia de caché a usar (por defecto InMemoryCache).
        """
        super().__init__(ttl, key_func)
        self.cache_instance = cache_instance or InMemoryCache()

    def __call__(self, func: F) -> F:
        """
        Aplica el decorador a la función.

        Parameters
        ----------
        func : Callable
            La función a decorar.

        Returns
        -------
        Callable
            La función decorada con caché automático.
        """

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generar clave de caché
            cache_key = self._generate_cache_key(func, args, kwargs)

            # Intentar obtener del caché
            if self.cache_instance.exists(cache_key):
                return self.cache_instance.get(cache_key)

            # Si no está en caché, ejecutar función
            result = func(*args, **kwargs)

            # Almacenar en caché
            self.cache_instance.set(cache_key, result, ttl=self.ttl)

            return result

        def clear_cache() -> None:
            """Limpia todo el caché de esta función."""
            # Para simplicidad, limpiamos todo el caché
            # En una implementación más sofisticada, podríamos limpiar solo
            # las claves de esta función específica
            self.cache_instance.clear()

        # Añadir metadatos de caché
        wrapper._is_cached = True  # type: ignore
        wrapper._cache_ttl = self.ttl  # type: ignore
        wrapper._cache_key_func = self.key_func  # type: ignore
        wrapper._cache_instance = self.cache_instance  # type: ignore
        wrapper.clear_cache = clear_cache  # type: ignore

        return wrapper  # type: ignore


class AsyncCache(BaseCacheDecorator):
    """
    Decorador para añadir caché automático a funciones asíncronas.

    Soporta funciones async def con operaciones de caché no bloqueantes,
    manejo de concurrencia y integración completa con asyncio.

    Para funciones síncronas, usar @Cache.
    Para detección automática, usar @SmartCache.
    """

    def __init__(
        self,
        ttl: timedelta | None = None,
        key_func: Callable[..., str] | None = None,
        cache_instance: Any = None,
    ) -> None:
        """
        Inicializa el decorador de caché asíncrono.

        Parameters
        ----------
        ttl : timedelta, optional
            Tiempo de vida del caché.
        key_func : Callable, optional
            Función personalizada para generar claves de caché.
        cache_instance : Any, optional
            Instancia de caché a usar (por defecto AsyncInMemoryCache).
        """
        super().__init__(ttl, key_func)
        # Importación tardía para evitar dependencias circulares
        if cache_instance is None:
            from .async_memory import AsyncInMemoryCache

            self.cache_instance = AsyncInMemoryCache()
        else:
            self.cache_instance = cache_instance
        # Diccionario para manejar operaciones concurrentes por clave
        self._pending_operations: dict[str, asyncio.Task[Any]] = {}

    def __call__(self, func: F) -> F:
        """
        Aplica el decorador a la función asíncrona.

        Parameters
        ----------
        func : Callable
            La función asíncrona a decorar.

        Returns
        -------
        Callable
            La función decorada con caché automático.
        """

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generar clave de caché
            cache_key = self._generate_cache_key(func, args, kwargs)

            # Intentar obtener del caché
            if await self.cache_instance.aexists(cache_key):
                return await self.cache_instance.aget(cache_key)

            # Verificar si hay una operación pendiente para esta clave
            if cache_key in self._pending_operations:
                # Esperar a que termine la operación pendiente
                try:
                    return await self._pending_operations[cache_key]
                except Exception:
                    # Si la operación pendiente falló, continuar con nueva ejecución
                    pass

            # Crear una nueva tarea para esta operación
            async def execute_and_cache() -> Any:
                try:
                    result = await func(*args, **kwargs)
                    await self.cache_instance.aset(cache_key, result, ttl=self.ttl)
                    return result
                finally:
                    # Limpiar la operación pendiente
                    self._pending_operations.pop(cache_key, None)

            # Crear y almacenar la tarea
            task = asyncio.create_task(execute_and_cache())
            self._pending_operations[cache_key] = task

            return await task

        async def aclear_cache() -> None:
            """Limpia todo el caché de esta función de forma asíncrona."""
            await self.cache_instance.aclear()

        # Añadir metadatos de caché
        async_wrapper._is_async_cached = True  # type: ignore
        async_wrapper._async_cache_ttl = self.ttl  # type: ignore
        async_wrapper._async_cache_key_func = self.key_func  # type: ignore
        async_wrapper._async_cache_instance = self.cache_instance  # type: ignore
        async_wrapper.aclear_cache = aclear_cache  # type: ignore

        return async_wrapper  # type: ignore


class SmartCache:
    """
    Decorador híbrido que detecta automáticamente si la función es síncrona o asíncrona.

    Aplica el decorador @Cache para funciones síncronas y @AsyncCache para asíncronas.
    """

    def __init__(
        self,
        ttl: timedelta | None = None,
        key_func: Callable[..., str] | None = None,
        sync_cache_instance: Any = None,
        async_cache_instance: Any = None,
    ) -> None:
        """
        Inicializa el decorador híbrido de caché.

        Parameters
        ----------
        ttl : timedelta, optional
            Tiempo de vida del caché.
        key_func : Callable, optional
            Función personalizada para generar claves de caché.
        sync_cache_instance : Any, optional
            Instancia de caché síncrono a usar.
        async_cache_instance : Any, optional
            Instancia de caché asíncrono a usar.
        """
        self.ttl = ttl
        self.key_func = key_func
        self.sync_cache_instance = sync_cache_instance
        self.async_cache_instance = async_cache_instance

    def __call__(self, func: F) -> F:
        """
        Aplica el decorador híbrido a la función.

        Parameters
        ----------
        func : Callable
            La función a decorar (puede ser sync o async).

        Returns
        -------
        Callable
            La función decorada con caché automático.
        """
        # Detectar si la función es asíncrona
        if inspect.iscoroutinefunction(func):
            # Función asíncrona - usar AsyncCache
            async_cache = AsyncCache(
                ttl=self.ttl,
                key_func=self.key_func,
                cache_instance=self.async_cache_instance,
            )
            decorated_func = async_cache(func)

            # Añadir metadatos específicos de SmartCache
            decorated_func._is_smart_cached = True  # type: ignore
            decorated_func._cache_type = "async"  # type: ignore

            return decorated_func
        else:
            # Función síncrona - usar Cache
            sync_cache = Cache(
                ttl=self.ttl,
                key_func=self.key_func,
                cache_instance=self.sync_cache_instance,
            )
            decorated_func = sync_cache(func)

            # Añadir metadatos específicos de SmartCache
            decorated_func._is_smart_cached = True  # type: ignore
            decorated_func._cache_type = "sync"  # type: ignore

            return decorated_func
