"""Unit tests for FinOpsCollector telemetry collection service."""

from collections.abc import AsyncGenerator
import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from generation.engine import NO_CONTEXT_REFUSAL, GroundedGenerator
from generation.finops import (
    FinOpsCollector,
    calculate_cost,
    count_tokens,
)
from models.chat import FinOpsMetadata



def test_count_tokens_valid_and_empty() -> None:
    """Verify count_tokens counts words/tokens accurately and returns 0 for empty strings."""
    assert count_tokens("") == 0
    assert count_tokens("Hello world") > 0
    assert count_tokens("Helvetia Consulting document assistant", "gpt-4o-mini") > 0
    assert count_tokens("Unknown model test", "nonexistent-model-xyz") > 0


def test_calculate_cost_models_and_cached() -> None:
    """Verify cost calculation across different models and cached requests."""
    cost_mini = calculate_cost(1000, 1000, model="gpt-4o-mini")
    assert cost_mini == round((1.0 * 0.00015) + (1.0 * 0.0006), 6)

    cost_4o = calculate_cost(1000, 500, model="gpt-4o")
    assert cost_4o == round((1.0 * 0.0025) + (0.5 * 0.01), 6)

    cost_cached = calculate_cost(1000, 1000, model="gpt-4o-mini", is_cached=True)
    assert cost_cached == 0.0

    cost_fallback = calculate_cost(1000, 1000, model="unknown-model")
    assert cost_fallback > 0.0


def test_finops_collector_collect_basic() -> None:
    """Verify FinOpsCollector collect constructs valid FinOpsMetadata payload."""
    collector = FinOpsCollector(default_model="gpt-4o-mini")
    meta = collector.collect(
        prompt_text="What is the policy?",
        completion_text="Compliance is mandatory.",
        execution_time_seconds=0.123,
    )
    assert isinstance(meta, FinOpsMetadata)
    assert meta.prompt_tokens > 0
    assert meta.completion_tokens > 0
    assert meta.total_tokens == meta.prompt_tokens + meta.completion_tokens
    assert meta.estimated_cost_usd > 0.0
    assert meta.execution_time_seconds == 0.123
    assert meta.is_cached is False


def test_finops_collector_collect_explicit_tokens() -> None:
    """Verify passing explicit token counts overrides automatic text counting."""
    collector = FinOpsCollector()
    meta = collector.collect(
        prompt_text="ignored text",
        completion_text="ignored text",
        execution_time_seconds=0.05,
        prompt_tokens=500,
        completion_tokens=200,
        is_cached=True,
    )
    assert meta.prompt_tokens == 500
    assert meta.completion_tokens == 200
    assert meta.total_tokens == 700
    assert meta.estimated_cost_usd == 0.0
    assert meta.is_cached is True


def test_finops_collector_track_latency() -> None:
    """Verify track_latency context manager measures execution duration."""
    collector = FinOpsCollector()
    with collector.track_latency() as metrics:
        time.sleep(0.01)

    assert "elapsed_seconds" in metrics
    assert metrics["elapsed_seconds"] >= 0.005


@pytest.mark.asyncio
async def test_grounded_generator_generate_with_finops() -> None:
    """Verify GroundedGenerator.generate_with_finops returns text and FinOpsMetadata."""
    mock_client = MagicMock()

    class MockChoiceDelta:
        def __init__(self, content: str | None) -> None:
            self.content = content

    class MockChoice:
        def __init__(self, content: str | None) -> None:
            self.delta = MockChoiceDelta(content)

    class MockChunk:
        def __init__(self, content: str | None) -> None:
            self.choices = [MockChoice(content)]

    async def mock_stream_iter() -> AsyncGenerator[MockChunk, None]:
        yield MockChunk("Grounded ")
        yield MockChunk("answer.")

    mock_client.chat.completions.create = AsyncMock(return_value=mock_stream_iter())

    gen = GroundedGenerator(client=mock_client, model="gpt-4o-mini")
    contexts = [{"file_name": "policy.pdf", "page_number": 1, "text": "Policy rules."}]

    answer, finops = await gen.generate_with_finops("Query", contexts)
    assert answer == "Grounded answer."
    assert isinstance(finops, FinOpsMetadata)
    assert finops.prompt_tokens > 0
    assert finops.completion_tokens > 0
    assert finops.execution_time_seconds >= 0.0


@pytest.mark.asyncio
async def test_grounded_generator_generate_with_finops_empty_contexts() -> None:
    """Verify generate_with_finops handles empty contexts refusal path."""
    mock_client = MagicMock()
    gen = GroundedGenerator(client=mock_client)

    answer, finops = await gen.generate_with_finops("Query", [])
    assert answer == NO_CONTEXT_REFUSAL
    assert finops.prompt_tokens == 0
    assert finops.completion_tokens == 0
    assert finops.estimated_cost_usd == 0.0
    assert finops.execution_time_seconds >= 0.0
