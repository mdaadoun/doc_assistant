"""Abstract base store interface for cache persistence layers."""

from abc import ABC, abstractmethod

from models.cache import CacheEntry, CacheStats


class BaseCacheStore(ABC):
    """Abstract interface defining required operations for cache backends."""

    @abstractmethod
    async def get(self, key: str) -> CacheEntry | None:
        """Retrieve a cached entry by its SHA-256 key, or None if missing/expired."""
        raise NotImplementedError

    @abstractmethod
    async def set(self, entry: CacheEntry) -> None:
        """Store or overwrite a cache entry."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Remove a cached entry by key. Returns True if removed, False otherwise."""
        raise NotImplementedError

    @abstractmethod
    async def clear(self) -> None:
        """Purge all stored cache entries."""
        raise NotImplementedError

    @abstractmethod
    async def has(self, key: str) -> bool:
        """Check if a non-expired entry exists for the given key."""
        raise NotImplementedError

    @abstractmethod
    async def size(self) -> int:
        """Return the current count of active cached entries."""
        raise NotImplementedError

    @abstractmethod
    async def get_stats(self) -> CacheStats:
        """Return current cache telemetry and operational statistics."""
        raise NotImplementedError

    @abstractmethod
    async def evict_expired(self) -> int:
        """Evict all expired cache entries and return the count of evicted items."""
        raise NotImplementedError
