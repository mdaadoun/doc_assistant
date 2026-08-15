"""Unit tests for GroundedGenerator LLM generation service."""

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest

from core.exceptions import ConfigurationError, GenerationError
from generation.engine import NO_CONTEXT_REFUSAL, SYSTEM_PROMPT, GroundedGenerator


def test_grounded_generator_init_with_key() -> None:
    """Verify generator initializes properly when explicit API key is provided."""
    gen = GroundedGenerator(
        api_key="test-openai-key", model="gpt-4o-mini", temperature=0.0
    )
    assert gen.model == "gpt-4o-mini"
    assert gen.temperature == 0.0


def test_grounded_generator_init_missing_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify ConfigurationError is raised when no API key is available."""
    monkeypatch.setenv("OPENAI_API_KEY", "")
    from core.config import clear_settings_cache

    clear_settings_cache()
    with pytest.raises(ConfigurationError) as exc_info:
        GroundedGenerator(api_key="")
    assert "OpenAI API key is required" in str(exc_info.value)
    clear_settings_cache()


def test_format_context_dicts_and_objects() -> None:
    """Verify _format_context handles both dict and object context representations."""
    gen = GroundedGenerator(api_key="test-key")

    dict_ctx = {
        "file_name": "guidelines.pdf",
        "page_number": 3,
        "text": "Safety rules.",
    }

    class MockContextObj:
        file_name = "policy.docx"
        page_number = 12
        text = "Company policy."

    obj_ctx = MockContextObj()

    formatted = gen._format_context([dict_ctx, obj_ctx])
    assert "Source File: guidelines.pdf" in formatted
    assert "Page Number: 3" in formatted
    assert "Content: Safety rules." in formatted
    assert "Source File: policy.docx" in formatted
    assert "Page Number: 12" in formatted
    assert "Content: Company policy." in formatted


@pytest.mark.asyncio
async def test_generate_stream_empty_contexts() -> None:
    """Verify empty contexts list immediately yields refusal string without calling client."""
    mock_client = MagicMock()
    gen = GroundedGenerator(client=mock_client)

    tokens = []
    async for token in gen.generate_stream("What is the policy?", []):
        tokens.append(token)

    assert tokens == [NO_CONTEXT_REFUSAL]
    mock_client.chat.completions.create.assert_not_called()


@pytest.mark.asyncio
async def test_generate_stream_success() -> None:
    """Verify streaming generation yields expected token chunks and passes parameters."""
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
        for text in ["Helvetia ", "Consulting ", "policy ", "requires ", "compliance."]:
            yield MockChunk(text)

    mock_client.chat.completions.create = AsyncMock(return_value=mock_stream_iter())

    gen = GroundedGenerator(client=mock_client, model="gpt-4o-mini", temperature=0.0)
    contexts = [
        {"file_name": "manual.pdf", "page_number": 1, "text": "Compliance rule."}
    ]

    tokens = []
    async for token in gen.generate_stream("Summarize policy", contexts):
        tokens.append(token)

    full_ans = "".join(tokens)
    assert full_ans == "Helvetia Consulting policy requires compliance."
    mock_client.chat.completions.create.assert_awaited_once()

    _, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs["model"] == "gpt-4o-mini"
    assert kwargs["temperature"] == 0.0
    assert kwargs["stream"] is True
    assert kwargs["messages"][0]["role"] == "system"
    assert kwargs["messages"][0]["content"] == SYSTEM_PROMPT
    assert (
        "CONTEXT INFORMATION:\nSource File: manual.pdf"
        in kwargs["messages"][1]["content"]
    )


@pytest.mark.asyncio
async def test_generate_non_streaming_success() -> None:
    """Verify non-streaming generate method accumulates streaming tokens."""
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
        yield MockChunk("Full ")
        yield MockChunk("Answer.")

    mock_client.chat.completions.create = AsyncMock(return_value=mock_stream_iter())

    gen = GroundedGenerator(client=mock_client)
    answer = await gen.generate(
        "Test query", [{"file_name": "a.pdf", "page_number": 1, "text": "info"}]
    )
    assert answer == "Full Answer."


@pytest.mark.asyncio
async def test_generate_stream_api_error_raises_generation_error() -> None:
    """Verify OpenAI client failures raise GenerationError."""
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(
        side_effect=RuntimeError("API Connection Timeout")
    )

    gen = GroundedGenerator(client=mock_client)
    contexts = [{"file_name": "doc.pdf", "page_number": 1, "text": "content"}]

    with pytest.raises(GenerationError) as exc_info:
        async for _ in gen.generate_stream("Query", contexts):
            pass

    assert "LLM streaming generation failed" in str(exc_info.value)
