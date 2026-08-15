"""Unit tests for GET /api/v1/debug/retrieval diagnostic endpoint."""

from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from starlette.requests import Request

from api.app import create_app
from api.dependencies import get_debug_retrieval_builder
from models.retrieval import DebugRetrievalHit, DebugRetrievalResponse, RetrievalResult
from retrieval.debug_retrieval import DebugRetrievalBuilder


def _sample_debug_response() -> DebugRetrievalResponse:
    """Fixture returning a pre-built DebugRetrievalResponse."""
    return DebugRetrievalResponse(
        query="security policy",
        dense_hits=[
            DebugRetrievalHit(chunk_id="chk_1", score=0.92, rank=1, method="dense")
        ],
        sparse_hits=[
            DebugRetrievalHit(chunk_id="chk_2", score=12.5, rank=1, method="sparse")
        ],
        rrf_fused=[
            DebugRetrievalHit(chunk_id="chk_1", score=0.032, rank=1, method="rrf")
        ],
        final_reranked=[
            RetrievalResult(
                chunk_id="chk_1",
                text="Security policy excerpt",
                file_name="sec.pdf",
                page_number=2,
                relevance_score=0.95,
                retrieval_method="rerank",
            )
        ],
    )


def test_debug_retrieval_endpoint_success() -> None:
    """Verify GET /api/v1/debug/retrieval returns HTTP 200 with debug payload."""
    app = create_app()
    mock_builder = MagicMock(spec=DebugRetrievalBuilder)
    mock_builder.build.return_value = _sample_debug_response()

    def _override_debug_builder(request: Request) -> DebugRetrievalBuilder:
        return mock_builder

    app.dependency_overrides[get_debug_retrieval_builder] = _override_debug_builder

    client = TestClient(app)
    response = client.get(
        "/api/v1/debug/retrieval", params={"query": "security policy"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "security policy"
    assert len(data["dense_hits"]) == 1
    assert data["dense_hits"][0]["chunk_id"] == "chk_1"
    assert len(data["sparse_hits"]) == 1
    assert len(data["rrf_fused"]) == 1
    assert len(data["final_reranked"]) == 1


def test_debug_retrieval_endpoint_with_top_k_params() -> None:
    """Verify endpoint correctly forwards optional top_k parameters to debug builder."""
    app = create_app()
    mock_builder = MagicMock(spec=DebugRetrievalBuilder)
    mock_builder.build.return_value = _sample_debug_response()

    def _override_debug_builder(request: Request) -> DebugRetrievalBuilder:
        return mock_builder

    app.dependency_overrides[get_debug_retrieval_builder] = _override_debug_builder

    client = TestClient(app)
    params: dict[str, str | int] = {
        "query": "compliance",
        "dense_top_k": 20,
        "sparse_top_k": 15,
        "rrf_top_k": 10,
        "rerank_top_k": 5,
    }
    response = client.get("/api/v1/debug/retrieval", params=params)

    assert response.status_code == 200
    mock_builder.build.assert_called_once_with(
        query="compliance",
        dense_top_k=20,
        sparse_top_k=15,
        rrf_top_k=10,
        rerank_top_k=5,
    )


def test_debug_retrieval_endpoint_missing_query_validation() -> None:
    """Verify missing query parameter triggers HTTP 422 validation failure."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/debug/retrieval")
    assert response.status_code == 422


def test_debug_retrieval_endpoint_invalid_top_k_validation() -> None:
    """Verify top_k parameter less than 1 triggers HTTP 422 validation failure."""
    app = create_app()
    client = TestClient(app)

    response = client.get(
        "/api/v1/debug/retrieval", params={"query": "test", "dense_top_k": 0}
    )
    assert response.status_code == 422
