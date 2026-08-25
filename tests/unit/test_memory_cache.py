"""Unit tests for InMemoryCacheStore."""

import time

import pytest

from cache.memory_store import InMemoryCacheStore
from core.exceptions import CacheError
from models.cache import CacheEntry


@pytest.mark.asyncio
async def test_memory_cache_get_set_delete() -> None:
    """Verify basic lifecycle operations: set, get, delete, has, size."""
    store = InMemoryCacheStore(max_entries=10)
    key = "a" * 64

    entry = CacheEntry(
        key=key,
        input_text="Query",
        prompt="Prompt",
        model="gpt-4o-mini",
        response="Answer A",
        created_at=time.time(),
    )

    assert await store.get(key) is None
    assert await store.has(key) is False
    assert await store.size() == 0

    await store.set(entry)
    assert await store.has(key) is True
    assert await store.size() == 1

    retrieved = await store.get(key)
    assert retrieved is not None
    assert retrieved.response == "Answer A"

    # Delete
    deleted = await store.delete(key)
    assert deleted is True
    assert await store.get(key) is None
    assert await store.has(key) is False
    assert await store.size() == 0

    # Delete non-existent
    assert await store.delete("nonexistent" + "0" * 53) is False


@pytest.mark.asyncio
async def test_memory_cache_lru_eviction() -> None:
    """Verify LRU entry eviction when capacity is exceeded."""
    store = InMemoryCacheStore(max_entries=2)

    entry1 = CacheEntry(
        key="1" * 64,
        input_text="Q1",
        prompt="P1",
        model="gpt-4o-mini",
        response="A1",
        created_at=time.time(),
    )
    entry2 = CacheEntry(
        key="2" * 64,
        input_text="Q2",
        prompt="P2",
        model="gpt-4o-mini",
        response="A2",
        created_at=time.time(),
    )
    entry3 = CacheEntry(
        key="3" * 64,
        input_text="Q3",
        prompt="P3",
        model="gpt-4o-mini",
        response="A3",
        created_at=time.time(),
    )

    await store.set(entry1)
    await store.set(entry2)

    # Access entry1 to make entry2 least-recently-used
    await store.get(entry1.key)

    # Adding entry3 should evict entry2
    await store.set(entry3)

    assert await store.get(entry1.key) is not None
    assert await store.get(entry2.key) is None
    assert await store.get(entry3.key) is not None
    assert await store.size() == 2


@pytest.mark.asyncio
async def test_memory_cache_ttl_expiration() -> None:
    """Verify expired entries return None and are pruned on access."""
    store = InMemoryCacheStore(max_entries=10)
    key = "t" * 64

    entry = CacheEntry(
        key=key,
        input_text="Query",
        prompt="Prompt",
        model="gpt-4o-mini",
        response="Expired Answer",
        created_at=time.time() - 100.0,
        ttl_seconds=10,  # expired
    )

    await store.set(entry)
    assert await store.has(key) is False
    assert await store.get(key) is None
    assert await store.size() == 0


@pytest.mark.asyncio
async def test_memory_cache_stats() -> None:
    """Verify hit rate and operational statistics tracking."""
    store = InMemoryCacheStore(max_entries=5)
    key = "s" * 64

    entry = CacheEntry(
        key=key,
        input_text="Query",
        prompt="Prompt",
        model="gpt-4o-mini",
        response="Stats Answer",
        created_at=time.time(),
    )

    await store.get("missing" + "0" * 57)  # miss 1
    await store.set(entry)
    await store.get(key)  # hit 1
    await store.get(key)  # hit 2

    stats = await store.get_stats()
    assert stats.hits == 2
    assert stats.misses == 1
    assert stats.entries_count == 1
    assert stats.hit_rate == round(2 / 3, 4)


@pytest.mark.asyncio
async def test_memory_cache_clear() -> None:
    """Verify clear empties all entries."""
    store = InMemoryCacheStore(max_entries=5)
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
    await store.clear()
    assert await store.size() == 0


def test_memory_cache_invalid_max_entries() -> None:
    """Verify CacheError raised when max_entries < 1."""
    with pytest.raises(CacheError) as exc_info:
        InMemoryCacheStore(max_entries=0)
    assert exc_info.value.code == "INVALID_CACHE_CONFIG"
