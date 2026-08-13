"""Unit tests for POST /api/v1/chat endpoint and ChatService execution."""

from collections.abc import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from starlette.requests import Request

from api.app import create_app
from api.dependencies import get_chat_service
from api.services.chat_service import ChatService
from models.chat import ChatRequest
from models.retrieval import RetrievalResult
from retrieval.confidence_guard import ConfidenceGuard


class MockGroundedGenerator:
    """Mock generator streaming predetermined token deltas."""

    async def generate_stream(
        self, query: str, contexts: list[RetrievalResult]
    ) -> AsyncGenerator[str, None]:
        """Stream sample answer deltas."""
        yield "Helvetia "
        yield "Consulting "
        yield "policy."


@pytest.fixture
def mock_retrieval_hits() -> list[RetrievalResult]:
    """Fixture providing high confidence candidate hits."""
    return [
        RetrievalResult(
            chunk_id="chk_101",
            text="Helvetia Consulting security policy handbook.",
            file_name="security_policy.pdf",
            page_number=4,
            relevance_score=0.88,
            retrieval_method="rrf",
        )
    ]


def test_chat_service_stream_chat_success(
    mock_retrieval_hits: list[RetrievalResult],
) -> None:
    """Verify ChatService streams metadata, tokens, and done events for valid confident prompt."""
    guard = ConfidenceGuard(threshold=0.35)
    generator = MockGroundedGenerator()  # type: ignore[assignment]
    service = ChatService(
        confidence_guard=guard,
        grounded_generator=generator,  # type: ignore[arg-type]
    )

    request = ChatRequest(query="What is the policy?", conversation_id="conv_100")

    async def _run_stream() -> list[str]:
        # Manually evaluate hits and stream via service logic
        decision = guard.evaluate(mock_retrieval_hits)
        token_stream = generator.generate_stream(request.query, decision.filtered_hits)
        frames: list[str] = []
        async for frame in service.sse_handler.stream_generator(
            token_stream=token_stream,
            conversation_id=request.conversation_id,
            confidence_score=decision.top_score,
            grounded=True,
            citations=[],
        ):
            frames.append(frame)
        return frames

    import asyncio

    frames = asyncio.run(_run_stream())
    combined = "".join(frames)

    assert "event: metadata" in combined
    assert "conv_100" in combined
    assert "event: token" in combined
    assert "Helvetia " in combined
    assert "event: done" in combined


def test_chat_endpoint_http_streaming_success(
    mock_retrieval_hits: list[RetrievalResult],
) -> None:
    """Verify POST /api/v1/chat endpoint returns SSE event stream with 200 OK."""
    app = create_app()

    class CustomChatService(ChatService):
        async def stream_chat(
            self, request: ChatRequest
        ) -> AsyncGenerator[str, None]:
            yield "event: metadata\ndata: {}\n\n"
            yield "event: token\ndata: {\"delta\": \"Answer\"}\n\n"
            yield "event: done\ndata: {\"status\": \"completed\"}\n\n"

    def _override_chat_service(request: Request) -> CustomChatService:
        return CustomChatService()

    app.dependency_overrides[get_chat_service] = _override_chat_service

    client = TestClient(app)
    response = client.post(
        "/api/v1/chat",
        json={
            "query": "What is the security policy?",
            "conversation_id": "conv_200",
            "top_k": 5,
        },
    )

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert "event: metadata" in response.text
    assert "event: token" in response.text
    assert "event: done" in response.text


def test_chat_endpoint_unconfident_refusal_stream() -> None:
    """Verify POST /api/v1/chat handles low confidence refusal response stream."""
    app = create_app()
    guard = ConfidenceGuard(threshold=0.90)
    service = ChatService(confidence_guard=guard)

    def _override_chat_service(request: Request) -> ChatService:
        return service

    app.dependency_overrides[get_chat_service] = _override_chat_service

    client = TestClient(app)
    response = client.post(
        "/api/v1/chat",
        json={"query": "Unknown topic?", "conversation_id": "conv_300"},
    )

    assert response.status_code == 200
    assert "event: metadata" in response.text
    assert "cannot answer this question" in response.text.lower()
    assert "event: done" in response.text


def test_chat_endpoint_invalid_request_validation() -> None:
    """Verify POST /api/v1/chat validates required fields and returns HTTP 422."""
    app = create_app()
    client = TestClient(app)

    response = client.post("/api/v1/chat", json={"query": ""})
    assert response.status_code == 422
