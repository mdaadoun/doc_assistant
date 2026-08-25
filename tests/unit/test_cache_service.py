"""Unit tests for ResponseCacheService high-level cache orchestrator."""

import pytest

from cache.service import ResponseCacheService
from models.chat import Citation


@pytest.mark.asyncio
async def test_cache_service_get_and_set() -> None:
    """Verify ResponseCacheService stores and retrieves responses with metadata and citations."""
    service = ResponseCacheService()
    citations = [
        Citation(
            file_name="travel_policy.pdf",
            page_number=4,
            chunk_id="chk-123",
            excerpt="Hotel bookings must use portal.",
            relevance_score=0.92,
        )
    ]

    # Miss initially
    miss = await service.get_response(
        input_text="How to book hotel?",
        prompt="SYSTEM: Follow guidelines.",
        model="gpt-4o-mini",
    )
    assert miss is None

    # Store
    entry = await service.set_response(
        input_text="How to book hotel?",
        prompt="SYSTEM: Follow guidelines.",
        model="gpt-4o-mini",
        response="Book via the corporate travel portal.",
        citations=citations,
        metadata={"cost_saved": 0.005},
    )
    assert len(entry.key) == 64
    assert entry.response == "Book via the corporate travel portal."

    # Hit
    hit = await service.get_response(
        input_text="How to book hotel?",
        prompt="SYSTEM: Follow guidelines.",
        model="gpt-4o-mini",
    )
    assert hit is not None
    assert hit.response == "Book via the corporate travel portal."
    assert len(hit.citations) == 1
    assert hit.citations[0].file_name == "travel_policy.pdf"
    assert hit.metadata["cost_saved"] == 0.005


@pytest.mark.asyncio
async def test_cache_service_disabled_bypass() -> None:
    """Verify when cache is disabled, lookups return None and storage is skipped."""
    service = ResponseCacheService(enabled=False)

    await service.set_response(
        input_text="Query",
        prompt="Prompt",
        model="gpt-4o-mini",
        response="Ignored",
    )
    assert await service.size() == 0

    hit = await service.get_response(
        input_text="Query",
        prompt="Prompt",
        model="gpt-4o-mini",
    )
    assert hit is None


@pytest.mark.asyncio
async def test_cache_service_invalidate_and_clear() -> None:
    """Verify invalidation by key parameters and total clearing."""
    service = ResponseCacheService()

    await service.set_response(
        input_text="Q1",
        prompt="P",
        model="gpt-4o-mini",
        response="A1",
    )
    await service.set_response(
        input_text="Q2",
        prompt="P",
        model="gpt-4o-mini",
        response="A2",
    )
    assert await service.size() == 2

    # Invalidate Q1
    removed = await service.invalidate(
        input_text="Q1",
        prompt="P",
        model="gpt-4o-mini",
    )
    assert removed is True
    assert await service.size() == 1
    assert (
        await service.get_response(input_text="Q1", prompt="P", model="gpt-4o-mini")
        is None
    )

    # Clear remaining
    await service.clear()
    assert await service.size() == 0
