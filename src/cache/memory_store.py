"""In-memory thread-safe cache store with LRU eviction and TTL support."""

import asyncio
import time
from collections import OrderedDict

import structlog

from cache.base import BaseCacheStore
from core.exceptions import CacheError
from models.cache import CacheEntry, CacheStats

logger = structlog.get_logger(__name__)


class InMemoryCacheStore(BaseCacheStore):
    """Asynchronous in-memory LRU cache store with TTL expiration."""

    def __init__(
        self,
        max_entries: int = 1000,
        default_ttl_seconds: int | None = None,
    ) -> None:
        """Initialize in-memory cache store with capacity and TTL bounds."""
        if max_entries < 1:
            raise CacheError(
                "max_entries must be greater than or equal to 1",
                code="INVALID_CACHE_CONFIG",
                details={"max_entries": max_entries},
            )
        self._max_entries = max_entries
        self._default_ttl = default_ttl_seconds
        self._store: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = asyncio.Lock()
        self._hits: int = 0
        self._misses: int = 0
        self._evictions: int = 0

    async def get(self, key: str) -> CacheEntry | None:
        """Retrieve entry by key and update LRU order, pruning if expired."""
        async with self._lock:
            try:
                if key not in self._store:
                    self._misses += 1
                    return None

                entry = self._store[key]
                if entry.is_expired():
                    del self._store[key]
                    self._misses += 1
                    self._evictions += 1
                    return None

                self._store.move_to_end(key)
                self._hits += 1
                return entry
            except Exception as err:
                raise CacheError(
                    f"In-memory cache retrieval error: {err}",
                    code="CACHE_READ_ERROR",
                    details={"key": key},
                ) from err

    async def set(self, entry: CacheEntry) -> None:
        """Store or update cache entry, performing LRU eviction if at capacity."""
        async with self._lock:
            try:
                if entry.key in self._store:
                    self._store.move_to_end(entry.key)
                    self._store[entry.key] = entry
                    return

                # Evict oldest entry if at capacity
                if len(self._store) >= self._max_entries:
                    self._store.popitem(last=False)
                    self._evictions += 1

                self._store[entry.key] = entry
            except Exception as err:
                raise CacheError(
                    f"In-memory cache write error: {err}",
                    code="CACHE_WRITE_ERROR",
                    details={"key": entry.key},
                ) from err

    async def delete(self, key: str) -> bool:
        """Delete an entry by key. Returns True if removed."""
        async with self._lock:
            try:
                if key in self._store:
                    del self._store[key]
                    return True
                return False
            except Exception as err:
                raise CacheError(
                    f"In-memory cache deletion error: {err}",
                    code="CACHE_DELETE_ERROR",
                    details={"key": key},
                ) from err

    async def clear(self) -> None:
        """Clear all entries in memory."""
        async with self._lock:
            try:
                self._store.clear()
            except Exception as err:
                raise CacheError(
                    f"In-memory cache clear error: {err}",
                    code="CACHE_CLEAR_ERROR",
                ) from err

    async def has(self, key: str) -> bool:
        """Check if active unexpired entry exists for key."""
        async with self._lock:
            try:
                if key not in self._store:
                    return False
                entry = self._store[key]
                if entry.is_expired():
                    del self._store[key]
                    self._evictions += 1
                    return False
                return True
            except Exception as err:
                raise CacheError(
                    f"In-memory cache lookup error: {err}",
                    code="CACHE_LOOKUP_ERROR",
                    details={"key": key},
                ) from err

    async def size(self) -> int:
        """Return active entries count after pruning expired ones."""
        await self.evict_expired()
        async with self._lock:
            return len(self._store)

    async def evict_expired(self) -> int:
        """Evict all expired entries and return number of evicted items."""
        async with self._lock:
            try:
                now = time.time()
                expired_keys = [k for k, v in self._store.items() if v.is_expired(now)]
                for k in expired_keys:
                    del self._store[k]
                    self._evictions += 1
                return len(expired_keys)
            except Exception as err:
                raise CacheError(
                    f"In-memory cache eviction error: {err}",
                    code="CACHE_EVICT_ERROR",
                ) from err

    async def get_stats(self) -> CacheStats:
        """Compute operational metrics and hit rate."""
        async with self._lock:
            total_lookups = self._hits + self._misses
            hit_rate = (self._hits / total_lookups) if total_lookups > 0 else 0.0
            return CacheStats(
                hits=self._hits,
                misses=self._misses,
                evictions=self._evictions,
                entries_count=len(self._store),
                hit_rate=round(hit_rate, 4),
            )
