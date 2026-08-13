"""Server-Sent Events (SSE) streaming response handler and frame formatter."""

import json
from collections.abc import AsyncGenerator, Sequence
from typing import Any

import structlog
from pydantic import BaseModel

from models.chat import (
    Citation,
    SSEDonePayload,
    SSEErrorPayload,
    SSEMetaDataPayload,
    SSETokenPayload,
)

logger = structlog.get_logger(__name__)


def format_sse_event(
    event: str | None = None,
    data: str | BaseModel | dict[str, Any] | list[Any] | None = None,
    event_id: str | None = None,
    retry: int | None = None,
) -> str:
    """Format inputs into W3C-compliant SSE event stream frame string."""
    buffer: list[str] = []

    if event_id is not None:
        buffer.append(f"id: {event_id}")
    if event is not None:
        buffer.append(f"event: {event}")
    if retry is not None:
        buffer.append(f"retry: {retry}")

    if data is not None:
        if isinstance(data, BaseModel):
            payload_str = data.model_dump_json()
        elif isinstance(data, (dict, list)):
            payload_str = json.dumps(data)
        else:
            payload_str = str(data)

        for line in payload_str.splitlines():
            buffer.append(f"data: {line}")
    else:
        buffer.append("data: ")

    return "\n".join(buffer) + "\n\n"


class SSEResponseHandler:
    """Handler for wrapping token streams into formatted Server-Sent Event streams."""

    def __init__(self, media_type: str = "text/event-stream") -> None:
        """Initialize SSE response handler with stream content media type."""
        self.media_type = media_type

    @staticmethod
    def format_frame(
        event: str | None = None,
        data: str | BaseModel | dict[str, Any] | list[Any] | None = None,
        event_id: str | None = None,
        retry: int | None = None,
    ) -> str:
        """Format an individual SSE event frame."""
        return format_sse_event(event=event, data=data, event_id=event_id, retry=retry)

    async def stream_generator(
        self,
        token_stream: AsyncGenerator[str, None],
        conversation_id: str,
        confidence_score: float = 1.0,
        grounded: bool = True,
        citations: Sequence[Citation | dict[str, Any]] | None = None,
    ) -> AsyncGenerator[str, None]:
        """Stream metadata, token deltas, and completion frames via SSE."""
        formatted_citations: list[Citation] = []
        if citations:
            for item in citations:
                if isinstance(item, Citation):
                    formatted_citations.append(item)
                elif isinstance(item, dict):
                    formatted_citations.append(Citation(**item))

        meta_payload = SSEMetaDataPayload(
            conversation_id=conversation_id,
            confidence_score=confidence_score,
            grounded=grounded,
            citations=formatted_citations,
        )
        yield self.format_frame(event="metadata", data=meta_payload)

        try:
            async for token in token_stream:
                token_payload = SSETokenPayload(delta=token)
                yield self.format_frame(event="token", data=token_payload)
        except Exception as err:
            logger.error("SSE stream generation encountered error", error=str(err))
            error_code = str(getattr(err, "code", "GENERATION_ERROR"))
            err_payload = SSEErrorPayload(error=str(err), code=error_code)
            yield self.format_frame(event="error", data=err_payload)

        done_payload = SSEDonePayload(status="completed", finish_reason="stop")
        yield self.format_frame(event="done", data=done_payload)

    async def stream_raw_tokens(
        self, token_stream: AsyncGenerator[str, None]
    ) -> AsyncGenerator[str, None]:
        """Stream raw data frames containing text token deltas directly."""
        try:
            async for token in token_stream:
                yield self.format_frame(data=token)
        except Exception as err:
            logger.error("Raw SSE token stream failed", error=str(err))
            err_payload = SSEErrorPayload(error=str(err))
            yield self.format_frame(event="error", data=err_payload)
