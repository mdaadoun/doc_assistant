"""Unit tests for CacheEntry and CacheStats domain models."""

import time

import pytest
from pydantic import ValidationError

from models.cache import CacheEntry, CacheStats
from models.chat import Citation


def test_cache_entry_instantiation_and_immutability() -> None:
    """Verify CacheEntry schema validation, immutability, and field constraints."""
    key = "a" * 64
    entry = CacheEntry(
        key=key,
        input_text="What are the expenses?",
        prompt="Instructions",
        model="gpt-4o-mini",
        response="Expenses are covered up to CHF 500.",
        created_at=time.time(),
        ttl_seconds=3600,
        citations=[
            Citation(
                file_name="expenses.pdf",
                page_number=2,
                chunk_id="chunk-1",
                excerpt="CHF 500 limit",
                relevance_score=0.95,
            )
        ],
        metadata={"token_count": 42},
    )

    assert entry.key == key
    assert entry.input_text == "What are the expenses?"
    assert len(entry.citations) == 1
    assert entry.citations[0].file_name == "expenses.pdf"
    assert entry.metadata["token_count"] == 42

    # Immutability check
    with pytest.raises(ValidationError):
        entry.response = "Mutated response"  # type: ignore[misc]


def test_cache_entry_invalid_key_length() -> None:
    """Verify validation error when key is not exactly 64 characters."""
    with pytest.raises(ValidationError):
        CacheEntry(
            key="short_key",
            input_text="Query",
            prompt="Prompt",
            model="gpt-4o-mini",
            response="Answer",
            created_at=time.time(),
        )


def test_cache_entry_is_expired_evaluation() -> None:
    """Verify is_expired correctly identifies active vs expired entries."""
    created = 1000.0
    entry_with_ttl = CacheEntry(
        key="b" * 64,
        input_text="Query",
        prompt="Prompt",
        model="gpt-4o-mini",
        response="Answer",
        created_at=created,
        ttl_seconds=60,
    )

    assert entry_with_ttl.is_expired(current_time=1030.0) is False
    assert entry_with_ttl.is_expired(current_time=1060.0) is False
    assert entry_with_ttl.is_expired(current_time=1061.0) is True

    entry_no_ttl = CacheEntry(
        key="c" * 64,
        input_text="Query",
        prompt="Prompt",
        model="gpt-4o-mini",
        response="Answer",
        created_at=created,
        ttl_seconds=None,
    )
    assert entry_no_ttl.is_expired(current_time=999999.0) is False


def test_cache_stats_metrics() -> None:
    """Verify CacheStats calculation and default values."""
    stats = CacheStats(
        hits=8,
        misses=2,
        evictions=1,
        entries_count=5,
        hit_rate=0.8,
    )
    assert stats.hits == 8
    assert stats.misses == 2
    assert stats.evictions == 1
    assert stats.entries_count == 5
    assert stats.hit_rate == 0.8
