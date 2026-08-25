"""Unit tests for GroundedGenerator integration with SHA-256 ResponseCacheService."""

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest

from cache.service import ResponseCacheService
from generation.engine import GroundedGenerator


class MockChoiceDelta:
    def __init__(self, content: str | None) -> None:
        self.content = content


class MockChoice:
    def __init__(self, content: str | None) -> None:
        self.delta = MockChoiceDelta(content)


class MockChunk:
    def __init__(self, content: str | None) -> None:
        self.choices = [MockChoice(content)]


@pytest.mark.asyncio
async def test_grounded_generator_cache_miss_then_hit() -> None:
    """Verify first query calls LLM and caches answer; second query hits cache and avoids LLM call."""
    mock_client = MagicMock()

    async def mock_stream_iter() -> AsyncGenerator[MockChunk, None]:
        yield MockChunk("Cached ")
        yield MockChunk("Answer.")

    mock_client.chat.completions.create = AsyncMock(return_value=mock_stream_iter())

    cache_service = ResponseCacheService()
    generator = GroundedGenerator(
        client=mock_client,
        model="gpt-4o-mini",
        cache_service=cache_service,
    )

    contexts = [{"file_name": "guidelines.pdf", "page_number": 1, "text": "Rules."}]
    query = "What are the rules?"

    # First call: cache miss -> calls LLM
    ans1, finops1 = await generator.generate_with_finops(query, contexts)
    assert ans1 == "Cached Answer."
    assert finops1.is_cached is False
    assert finops1.estimated_cost_usd > 0.0
    assert mock_client.chat.completions.create.call_count == 1

    # Second call: cache hit -> skips LLM, returns is_cached=True with $0.00 cost
    mock_client.chat.completions.create.reset_mock()
    ans2, finops2 = await generator.generate_with_finops(query, contexts)
    assert ans2 == "Cached Answer."
    assert finops2.is_cached is True
    assert finops2.prompt_tokens == 0
    assert finops2.completion_tokens == 0
    assert finops2.estimated_cost_usd == 0.0
    mock_client.chat.completions.create.assert_not_called()


@pytest.mark.asyncio
async def test_grounded_generator_streaming_cache_hit() -> None:
    """Verify streaming generation directly yields cached answer on hit."""
    mock_client = MagicMock()
    cache_service = ResponseCacheService()

    generator = GroundedGenerator(
        client=mock_client,
        model="gpt-4o-mini",
        cache_service=cache_service,
    )

    contexts = [{"file_name": "manual.pdf", "page_number": 2, "text": "Content."}]
    query = "Streaming query test"

    # Prepopulate cache
    context_str = generator._format_context(contexts)
    prompt = f"CONTEXT INFORMATION:\n{context_str}\n\nUSER QUESTION: {query}"
    full_prompt = f'You are a precise corporate assistant for Helvetia Consulting.\nYour task is to answer the user\'s question STRICTLY using the context blocks provided below.\n\nSTRICT RULES:\n1. Base your answer ONLY on clear facts directly mentioned in the Context. Do NOT use outside knowledge or assumptions.\n2. If the answer cannot be fully derived from the provided Context, state clearly: "I cannot answer this question based on the available documentation."\n3. For EVERY factual claim in your response, append an inline citation referencing the source file and page using this exact format: [Doc: <file_name> | Page: <page_number>].\n\n{prompt}'

    await cache_service.set_response(
        input_text=query,
        prompt=full_prompt,
        model="gpt-4o-mini",
        response="Immediate cached stream payload.",
    )

    tokens = []
    async for token in generator.generate_stream(query, contexts):
        tokens.append(token)

    assert "".join(tokens) == "Immediate cached stream payload."
    mock_client.chat.completions.create.assert_not_called()
