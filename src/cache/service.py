"""High-level application service for SHA-256 generation and retrieval response caching."""

import time
from typing import Any

import structlog

from cache.base import BaseCacheStore
from cache.key_generator import compute_cache_key
from cache.memory_store import InMemoryCacheStore
from models.cache import CacheEntry, CacheStats
from models.chat import Citation

logger = structlog.get_logger(__name__)


class ResponseCacheService:
    """Service managing deterministic response caching with SHA-256 digest keys."""

    def __init__(
        self,
        store: BaseCacheStore | None = None,
        default_ttl_seconds: int | None = 3600,
        enabled: bool = True,
    ) -> None:
        """Initialize cache service with backend store and configuration."""
        self.store = store or InMemoryCacheStore(
            default_ttl_seconds=default_ttl_seconds
        )
        self.default_ttl = default_ttl_seconds
        self.enabled = enabled

    def compute_key(
        self,
        input_text: str,
        prompt: str,
        model: str,
        extra_params: dict[str, Any] | None = None,
    ) -> str:
        """Derive 64-character SHA-256 cache key from input query, prompt, and model."""
        return compute_cache_key(
            input_text=input_text,
            prompt=prompt,
            model=model,
            extra_params=extra_params,
        )

    async def get_response(
        self,
        input_text: str,
        prompt: str,
        model: str,
        extra_params: dict[str, Any] | None = None,
    ) -> CacheEntry | None:
        """Lookup cached response by canonical parameters. Returns None on miss or disabled."""
        if not self.enabled:
            return None

        key = self.compute_key(
            input_text=input_text,
            prompt=prompt,
            model=model,
            extra_params=extra_params,
        )
        entry = await self.store.get(key)
        if entry is not None:
            logger.info(
                "cache_hit",
                key=key,
                model=model,
                input_preview=input_text[:50],
            )
        else:
            logger.debug(
                "cache_miss",
                key=key,
                model=model,
                input_preview=input_text[:50],
            )
        return entry

    async def set_response(
        self,
        input_text: str,
        prompt: str,
        model: str,
        response: str,
        citations: list[Citation] | None = None,
        ttl_seconds: int | None = None,
        metadata: dict[str, Any] | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> CacheEntry:
        """Store generation response under deterministic SHA-256 key."""
        key = self.compute_key(
            input_text=input_text,
            prompt=prompt,
            model=model,
            extra_params=extra_params,
        )
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl

        entry = CacheEntry(
            key=key,
            input_text=input_text,
            prompt=prompt,
            model=model,
            response=response,
            created_at=time.time(),
            ttl_seconds=ttl,
            citations=citations or [],
            metadata=metadata or {},
        )

        if self.enabled:
            await self.store.set(entry)
            logger.info(
                "cache_stored",
                key=key,
                model=model,
                ttl_seconds=ttl,
            )

        return entry

    async def invalidate(
        self,
        input_text: str,
        prompt: str,
        model: str,
        extra_params: dict[str, Any] | None = None,
    ) -> bool:
        """Remove a cached response entry matching key parameters."""
        key = self.compute_key(
            input_text=input_text,
            prompt=prompt,
            model=model,
            extra_params=extra_params,
        )
        return await self.store.delete(key)

    async def clear(self) -> None:
        """Purge all entries from the underlying cache store."""
        await self.store.clear()
        logger.info("cache_cleared")

    async def size(self) -> int:
        """Return total active entries stored in cache."""
        return await self.store.size()

    async def get_stats(self) -> CacheStats:
        """Return cache operational statistics."""
        return await self.store.get_stats()
