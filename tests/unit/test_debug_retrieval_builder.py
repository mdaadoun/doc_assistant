"""Unit tests for DebugRetrievalBuilder (feature 5.4 debug data structure)."""

from unittest.mock import MagicMock

from models.retrieval import DebugRetrievalHit, DebugRetrievalResponse, RetrievalResult
from retrieval.debug_retrieval import DebugRetrievalBuilder


def _make_result(
    chunk_id: str,
    score: float,
    method: str = "dense",
) -> RetrievalResult:
    """Build a RetrievalResult fixture."""
    return RetrievalResult(
        chunk_id=chunk_id,
        text="sample text",
        file_name="policy.pdf",
        page_number=1,
        relevance_score=score,
        retrieval_method=method,
    )


def _make_builder(
    dense_hits: list[RetrievalResult],
    sparse_hits: list[RetrievalResult],
    fused_hits: list[RetrievalResult],
) -> DebugRetrievalBuilder:
    """Construct builder with mocked dense, sparse, and RRF services."""
    dense = MagicMock()
    dense.search.return_value = dense_hits
    sparse = MagicMock()
    sparse.search.return_value = sparse_hits
    rrf = MagicMock()
    rrf.fuse.return_value = fused_hits
    return DebugRetrievalBuilder(
        dense_search=dense,
        sparse_search=sparse,
        rrf_fusion=rrf,
    )


def test_build_populates_all_stage_hits() -> None:
    """Verify build exposes dense scores, sparse scores, and fused ranks."""
    dense_hits = [
        _make_result("a", 0.9),
        _make_result("b", 0.8),
    ]
    sparse_hits = [
        _make_result("b", 14.8, method="sparse"),
        _make_result("c", 11.2, method="sparse"),
    ]
    fused_hits = [
        _make_result("b", 0.0327, method="rrf"),
        _make_result("a", 0.0164, method="rrf"),
    ]

    builder = _make_builder(dense_hits, sparse_hits, fused_hits)
    response = builder.build("insurance coverage")

    assert isinstance(response, DebugRetrievalResponse)
    assert response.query == "insurance coverage"

    assert response.dense_hits == [
        DebugRetrievalHit(chunk_id="a", score=0.9, rank=1, method="dense"),
        DebugRetrievalHit(chunk_id="b", score=0.8, rank=2, method="dense"),
    ]
    assert response.sparse_hits == [
        DebugRetrievalHit(chunk_id="b", score=14.8, rank=1, method="sparse"),
        DebugRetrievalHit(chunk_id="c", score=11.2, rank=2, method="sparse"),
    ]
    assert response.rrf_fused == [
        DebugRetrievalHit(chunk_id="b", score=0.0327, rank=1, method="rrf"),
        DebugRetrievalHit(chunk_id="a", score=0.0164, rank=2, method="rrf"),
    ]
    assert response.final_reranked == []


def test_build_forwards_top_k_parameters() -> None:
    """Verify per-stage top_k values are forwarded to underlying services."""
    builder = _make_builder([], [], [])
    builder.build(
        "query",
        dense_top_k=10,
        sparse_top_k=20,
        rrf_top_k=5,
    )

    assert builder.dense_search is not None
    assert builder.sparse_search is not None
    assert builder.rrf_fusion is not None
    builder.dense_search.search.assert_called_once_with("query", top_k=10)  # type: ignore[attr-defined]
    builder.sparse_search.search.assert_called_once_with("query", top_k=20)  # type: ignore[attr-defined]
    builder.rrf_fusion.fuse.assert_called_once_with(  # type: ignore[attr-defined]
        dense_hits=[], sparse_hits=[], top_k=5
    )


def test_build_empty_pipeline_returns_empty_stages() -> None:
    """Verify build with no hits returns empty debug stage lists."""
    builder = _make_builder([], [], [])
    response = builder.build("empty query")

    assert response.dense_hits == []
    assert response.sparse_hits == []
    assert response.rrf_fused == []
    assert response.final_reranked == []
