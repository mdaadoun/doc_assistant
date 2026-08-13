"""Unit tests for Server-Sent Events (SSE) streaming response handler."""

from collections.abc import AsyncGenerator

import pytest

from generation.sse import SSEResponseHandler, format_sse_event
from models.chat import (
    Citation,
    SSEDonePayload,
    SSEErrorPayload,
    SSEMetaDataPayload,
    SSETokenPayload,
)


def test_format_sse_event_basic_string() -> None:
    """Verify formatting basic data string into SSE frame."""
    frame = format_sse_event(data="hello world")
    assert frame == "data: hello world\n\n"


def test_format_sse_event_with_event_and_id() -> None:
    """Verify formatting SSE frame with event name, ID, and retry."""
    frame = format_sse_event(
        event="token", data="sample delta", event_id="chunk-123", retry=3000
    )
    assert "id: chunk-123\n" in frame
    assert "event: token\n" in frame
    assert "retry: 3000\n" in frame
    assert "data: sample delta\n\n" in frame


def test_format_sse_event_multiline_string() -> None:
    """Verify formatting multi-line string into separate data lines in SSE frame."""
    frame = format_sse_event(data="line1\nline2")
    assert frame == "data: line1\ndata: line2\n\n"


def test_format_sse_event_pydantic_model() -> None:
    """Verify formatting Pydantic domain model into JSON SSE data frame."""
    payload = SSETokenPayload(delta="token_abc")
    frame = format_sse_event(event="token", data=payload)
    assert "event: token\n" in frame
    assert 'data: {"delta":"token_abc"}\n\n' in frame


def test_format_sse_event_dict_and_list() -> None:
    """Verify formatting dict and list structures into JSON SSE data frames."""
    dict_frame = format_sse_event(data={"key": "val"})
    assert 'data: {"key": "val"}\n\n' in dict_frame

    list_frame = format_sse_event(data=[1, 2, 3])
    assert "data: [1, 2, 3]\n\n" in list_frame


def test_format_sse_event_none_data() -> None:
    """Verify formatting None data into empty data SSE frame."""
    frame = format_sse_event(event="ping", data=None)
    assert frame == "event: ping\ndata: \n\n"


@pytest.mark.asyncio
async def test_sse_handler_stream_generator_success() -> None:
    """Verify SSEResponseHandler streams metadata, token deltas, and completion frames."""
    handler = SSEResponseHandler()
    assert handler.media_type == "text/event-stream"

    async def mock_token_generator() -> AsyncGenerator[str, None]:
        yield "Hello "
        yield "world!"

    citation_dict = {
        "file_name": "policy.pdf",
        "page_number": 2,
        "chunk_id": "c-1",
        "excerpt": "Excerpt text",
        "relevance_score": 0.95,
    }

    frames: list[str] = []
    async for frame in handler.stream_generator(
        token_stream=mock_token_generator(),
        conversation_id="conv-100",
        confidence_score=0.95,
        grounded=True,
        citations=[citation_dict],
    ):
        frames.append(frame)

    assert len(frames) == 4

    # 1. Metadata frame
    assert "event: metadata\n" in frames[0]
    assert "conv-100" in frames[0]
    assert "policy.pdf" in frames[0]

    # 2. Token frames
    assert "event: token\n" in frames[1]
    assert '"delta":"Hello "' in frames[1]
    assert "event: token\n" in frames[2]
    assert '"delta":"world!"' in frames[2]

    # 3. Done frame
    assert "event: done\n" in frames[3]
    assert '"status":"completed"' in frames[3]


@pytest.mark.asyncio
async def test_sse_handler_stream_generator_error_handling() -> None:
    """Verify SSEResponseHandler yields error frame when token stream fails."""
    handler = SSEResponseHandler()

    async def failing_token_generator() -> AsyncGenerator[str, None]:
        yield "Start token "
        raise RuntimeError("Stream interrupted")

    frames: list[str] = []
    async for frame in handler.stream_generator(
        token_stream=failing_token_generator(),
        conversation_id="conv-200",
    ):
        frames.append(frame)

    assert len(frames) == 4
    assert "event: metadata\n" in frames[0]
    assert "event: token\n" in frames[1]

    # Error frame
    assert "event: error\n" in frames[2]
    assert "Stream interrupted" in frames[2]
    assert "GENERATION_ERROR" in frames[2]

    # Done frame
    assert "event: done\n" in frames[3]


@pytest.mark.asyncio
async def test_sse_handler_stream_raw_tokens() -> None:
    """Verify streaming raw data-only frames for tokens."""
    handler = SSEResponseHandler()

    async def mock_token_generator() -> AsyncGenerator[str, None]:
        yield "Alpha "
        yield "Beta"

    frames: list[str] = []
    async for frame in handler.stream_raw_tokens(mock_token_generator()):
        frames.append(frame)

    assert len(frames) == 2
    assert frames[0] == "data: Alpha \n\n"
    assert frames[1] == "data: Beta\n\n"


@pytest.mark.asyncio
async def test_sse_handler_stream_raw_tokens_error() -> None:
    """Verify raw stream handles error gracefully by yielding error frame."""
    handler = SSEResponseHandler()

    async def failing_generator() -> AsyncGenerator[str, None]:
        raise ValueError("Connection closed")
        yield "unreachable"  # pragma: no cover

    frames: list[str] = []
    async for frame in handler.stream_raw_tokens(failing_generator()):
        frames.append(frame)

    assert len(frames) == 1
    assert "event: error\n" in frames[0]
    assert "Connection closed" in frames[0]
