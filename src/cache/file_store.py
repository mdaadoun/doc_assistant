"""Persistent file-based cache store with atomic writes and TTL expiration."""

import asyncio
import contextlib
import json
import time
from pathlib import Path

import structlog

from cache.base import BaseCacheStore
from core.exceptions import CacheError
from models.cache import CacheEntry, CacheStats

logger = structlog.get_logger(__name__)


class FileCacheStore(BaseCacheStore):
    """File-backed persistent cache storing serialized JSON entries per SHA-256 key."""

    def __init__(self, cache_dir: Path | str = ".cache/responses") -> None:
        """Initialize file cache directory and internal lock."""
        self.cache_dir = Path(cache_dir)
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception as err:
            raise CacheError(
                f"Failed to initialize cache directory {self.cache_dir}: {err}",
                code="CACHE_INIT_ERROR",
                details={"cache_dir": str(self.cache_dir)},
            ) from err

        self._lock = asyncio.Lock()
        self._hits: int = 0
        self._misses: int = 0
        self._evictions: int = 0

    def _get_entry_path(self, key: str) -> Path:
        """Derive filesystem path for a given SHA-256 key."""
        return self.cache_dir / f"{key}.json"

    async def get(self, key: str) -> CacheEntry | None:
        """Read and deserialize cache entry from disk, evicting if expired."""
        async with self._lock:
            path = self._get_entry_path(key)
            if not path.is_file():
                self._misses += 1
                return None

            try:
                content = path.read_text(encoding="utf-8")
                entry = CacheEntry.model_validate_json(content)

                if entry.is_expired():
                    with contextlib.suppress(OSError):
                        path.unlink(missing_ok=True)
                    self._misses += 1
                    self._evictions += 1
                    return None

                self._hits += 1
                return entry
            except Exception as err:
                logger.warning(
                    "Corrupted cache file encountered",
                    path=str(path),
                    error=str(err),
                )
                with contextlib.suppress(OSError):
                    path.unlink(missing_ok=True)
                self._misses += 1
                return None

    async def set(self, entry: CacheEntry) -> None:
        """Persist cache entry to disk atomically via temporary file replacement."""
        async with self._lock:
            target_path = self._get_entry_path(entry.key)
            tmp_path = self.cache_dir / f"{entry.key}.tmp"
            try:
                payload = entry.model_dump_json(indent=2)
                tmp_path.write_text(payload, encoding="utf-8")
                tmp_path.replace(target_path)
            except Exception as err:
                if tmp_path.is_file():
                    with contextlib.suppress(OSError):
                        tmp_path.unlink(missing_ok=True)
                raise CacheError(
                    f"Failed to write cache entry to disk: {err}",
                    code="CACHE_WRITE_ERROR",
                    details={"key": entry.key, "path": str(target_path)},
                ) from err

    async def delete(self, key: str) -> bool:
        """Remove cache file by key. Returns True if deleted."""
        async with self._lock:
            path = self._get_entry_path(key)
            if path.is_file():
                try:
                    path.unlink()
                    return True
                except Exception as err:
                    raise CacheError(
                        f"Failed to delete cache file {path}: {err}",
                        code="CACHE_DELETE_ERROR",
                        details={"key": key},
                    ) from err
            return False

    async def clear(self) -> None:
        """Purge all cache json files in the directory."""
        async with self._lock:
            try:
                for file_path in self.cache_dir.glob("*.json"):
                    with contextlib.suppress(OSError):
                        file_path.unlink(missing_ok=True)
            except Exception as err:
                raise CacheError(
                    f"Failed to clear cache directory: {err}",
                    code="CACHE_CLEAR_ERROR",
                ) from err

    async def has(self, key: str) -> bool:
        """Check whether valid non-expired file exists for key."""
        entry = await self.get(key)
        return entry is not None

    async def size(self) -> int:
        """Count active unexpired entries on disk."""
        await self.evict_expired()
        async with self._lock:
            return len(list(self.cache_dir.glob("*.json")))

    async def evict_expired(self) -> int:
        """Scan directory and remove expired entry files."""
        async with self._lock:
            evicted = 0
            now = time.time()
            for file_path in list(self.cache_dir.glob("*.json")):
                try:
                    content = file_path.read_text(encoding="utf-8")
                    data = json.loads(content)
                    created_at = float(data.get("created_at", 0))
                    ttl = data.get("ttl_seconds")
                    if ttl is not None and (now - created_at) > ttl:
                        file_path.unlink(missing_ok=True)
                        evicted += 1
                        self._evictions += 1
                except Exception:
                    file_path.unlink(missing_ok=True)
                    evicted += 1
            return evicted

    async def get_stats(self) -> CacheStats:
        """Return cache operational metrics."""
        async with self._lock:
            total_lookups = self._hits + self._misses
            hit_rate = (self._hits / total_lookups) if total_lookups > 0 else 0.0
            entries_count = len(list(self.cache_dir.glob("*.json")))
            return CacheStats(
                hits=self._hits,
                misses=self._misses,
                evictions=self._evictions,
                entries_count=entries_count,
                hit_rate=round(hit_rate, 4),
            )
