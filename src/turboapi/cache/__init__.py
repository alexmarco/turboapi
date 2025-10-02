"""Módulo de caché."""

from .async_memory import AsyncInMemoryCache
from .context import AsyncCacheContext
from .context import AsyncCacheManager
from .context import clear_global_cache
from .context import get_global_cache
from .context import get_global_cache_stats
from .decorators import AsyncCache
from .decorators import BaseCacheDecorator
from .decorators import Cache
from .decorators import SmartCache
from .memory import InMemoryCache
from .starter import CacheStarter

__all__ = [
    "InMemoryCache",
    "AsyncInMemoryCache",
    "BaseCacheDecorator",
    "Cache",
    "AsyncCache",
    "SmartCache",
    "CacheStarter",
    "AsyncCacheContext",
    "AsyncCacheManager",
    "get_global_cache",
    "clear_global_cache",
    "get_global_cache_stats",
]
