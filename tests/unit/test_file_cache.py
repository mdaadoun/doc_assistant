"""Unit tests for FileCacheStore persistent cache implementation."""

import time
from pathlib import Path

import pytest

from cache.file_store import FileCacheStore
from models.cache import CacheEntry


@pytest.mark.asyncio
async def test_file_cache_lifecycle(tmp_path: Path) -> None:
    """Verify file-based cache lifecycle: set, get, persistence, delete, size."""
    cache_dir = tmp_path / "cache_store"
    store = FileCacheStore(cache_dir=cache_dir)
    key = "f" * 64

    entry = CacheEntry(
        key=key,
        input_text="Test input",
        prompt="Test prompt",
        model="gpt-4o-mini",
        response="File cached answer",
        created_at=time.time(),
        ttl_seconds=3600,
    )

    assert await store.get(key) is None
    assert await store.size() == 0

    await store.set(entry)
    assert (cache_dir / f"{key}.json").is_file()
    assert await store.size() == 1
    assert await store.has(key) is True

    # Read back
    retrieved = await store.get(key)
    assert retrieved is not None
    assert retrieved.response == "File cached answer"
    assert retrieved.input_text == "Test input"

    # Delete
    deleted = await store.delete(key)
    assert deleted is True
    assert not (cache_dir / f"{key}.json").is_file()
    assert await store.get(key) is None
    assert await store.size() == 0


@pytest.mark.asyncio
async def test_file_cache_ttl_expiration(tmp_path: Path) -> None:
    """Verify expired file entries are ignored and unlinked on lookup."""
    cache_dir = tmp_path / "cache_ttl"
    store = FileCacheStore(cache_dir=cache_dir)
    key = "e" * 64

    entry = CacheEntry(
        key=key,
        input_text="Expired input",
        prompt="Prompt",
        model="gpt-4o-mini",
        response="Expired",
        created_at=time.time() - 200.0,
        ttl_seconds=10,
    )

    await store.set(entry)
    assert (cache_dir / f"{key}.json").is_file()

    retrieved = await store.get(key)
    assert retrieved is None
    assert not (cache_dir / f"{key}.json").is_file()


@pytest.mark.asyncio
async def test_file_cache_corrupted_file_handling(tmp_path: Path) -> None:
    """Verify corrupted JSON files return None and get cleaned up safely."""
    cache_dir = tmp_path / "cache_corrupt"
    store = FileCacheStore(cache_dir=cache_dir)
    key = "c" * 64
    corrupt_file = cache_dir / f"{key}.json"
    corrupt_file.write_text("CORRUPTED INVALID JSON {{{{", encoding="utf-8")

    retrieved = await store.get(key)
    assert retrieved is None
    assert not corrupt_file.is_file()


@pytest.mark.asyncio
async def test_file_cache_clear_and_stats(tmp_path: Path) -> None:
    """Verify clear purges directory and stats compute accurately."""
    cache_dir = tmp_path / "cache_stats"
    store = FileCacheStore(cache_dir=cache_dir)

    for i in range(3):
        k = str(i) * 64
        await store.set(
            CacheEntry(
                key=k,
                input_text=f"Q{i}",
                prompt="P",
                model="gpt-4o-mini",
                response=f"A{i}",
                created_at=time.time(),
            )
        )

    assert await store.size() == 3

    # Hits and misses
    await store.get("0" * 64)  # hit
    await store.get("9" * 64)  # miss

    stats = await store.get_stats()
    assert stats.hits == 1
    assert stats.misses == 1
    assert stats.entries_count == 3
    assert stats.hit_rate == 0.5

    await store.clear()
    assert await store.size() == 0
