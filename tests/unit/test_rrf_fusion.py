"""Unit tests for Reciprocal Rank Fusion service (feature 5.3, k=60)."""

import pytest

from models.retrieval import RetrievalResult
from retrieval.rrf_fusion import (
    RRF_K_DEFAULT,
    RRF_METHOD,
    RRF_TOP_K_DEFAULT,
    RRFusionService,
)


def _make_hit(
    chunk_id: str,
    text: str = "sample text",
    file_name: str = "policy.pdf",
    page_number: int = 1,
    score: float = 1.0,
    method: str = "dense",
) -> RetrievalResult:
    """Build a RetrievalResult fixture."""
    return RetrievalResult(
        chunk_id=chunk_id,
        text=text,
        file_name=file_name,
        page_number=page_number,
        relevance_score=score,
        retrieval_method=method,
    )


def test_default_constants() -> None:
    """Verify feature requirement defaults: k=60, top 50, method rrf."""
    assert RRF_K_DEFAULT == 60
    assert RRF_TOP_K_DEFAULT == 50
    assert RRF_METHOD == "rrf"


def test_init_defaults_and_clamping() -> None:
    """Verify k and top_k default and clamp non-positive values to 1."""
    service = RRFusionService()
    assert service.k == 60
    assert service.top_k == 50

    service = RRFusionService(k=0, top_k=0)
    assert service.k == 1
    assert service.top_k == 1

    service = RRFusionService(k=-5, top_k=-10)
    assert service.k == 1
    assert service.top_k == 1


def test_fuse_merges_and_ranks_by_rrf_score() -> None:
    """Verify RRF ranks shared hits higher and preserves unique hits."""
    dense = [
        _make_hit("a", score=0.9),
        _make_hit("b", score=0.8),
        _make_hit("c", score=0.7),
    ]
    sparse = [
        _make_hit("b", score=0.6, method="sparse"),
        _make_hit("c", score=0.5, method="sparse"),
        _make_hit("d", score=0.4, method="sparse"),
    ]

    service = RRFusionService()
    fused = service.fuse(dense_hits=dense, sparse_hits=sparse)

    assert len(fused) == 4
    assert fused[0].chunk_id == "b"
    assert fused[1].chunk_id == "c"
    assert {r.chunk_id for r in fused} == {"a", "b", "c", "d"}
    assert all(r.retrieval_method == "rrf" for r in fused)
    assert fused[0].relevance_score > fused[1].relevance_score


def test_fuse_uses_reciprocal_rank_formula() -> None:
    """Verify RRF score equals sum of 1/(k+rank) across lists."""
    dense = [_make_hit("x", score=0.9)]
    sparse = [_make_hit("x", score=0.8, method="sparse")]

    service = RRFusionService(k=60)
    fused = service.fuse(dense_hits=dense, sparse_hits=sparse)

    expected = 1.0 / (60 + 1) + 1.0 / (60 + 1)
    assert fused[0].relevance_score == pytest.approx(expected)


def test_fuse_returns_top_k() -> None:
    """Verify fused output is limited to top_k."""
    dense = [_make_hit(f"d_{i}") for i in range(10)]
    sparse = [_make_hit(f"s_{i}", method="sparse") for i in range(10)]

    service = RRFusionService(top_k=5)
    fused = service.fuse(dense_hits=dense, sparse_hits=sparse)

    assert len(fused) == 5


def test_fuse_custom_top_k_overrides_default() -> None:
    """Verify per-call top_k overrides configured default."""
    dense = [_make_hit(f"d_{i}") for i in range(10)]
    sparse = [_make_hit(f"s_{i}", method="sparse") for i in range(10)]

    service = RRFusionService(top_k=50)
    fused = service.fuse(dense_hits=dense, sparse_hits=sparse, top_k=3)

    assert len(fused) == 3


def test_fuse_empty_lists_returns_empty() -> None:
    """Verify fusing two empty lists returns an empty list."""
    service = RRFusionService()
    assert service.fuse(dense_hits=[], sparse_hits=[]) == []


def test_fuse_single_list_only() -> None:
    """Verify fusion works when only one list is provided."""
    dense = [_make_hit("a"), _make_hit("b")]

    service = RRFusionService()
    fused = service.fuse(dense_hits=dense, sparse_hits=[])

    assert len(fused) == 2
    assert fused[0].chunk_id == "a"
    assert fused[1].chunk_id == "b"
    assert all(r.retrieval_method == "rrf" for r in fused)


def test_fuse_dense_payload_preferred_on_duplicate() -> None:
    """Verify dense hit payload is used when a chunk appears in both lists."""
    dense = [_make_hit("a", text="dense text", file_name="dense.pdf")]
    sparse = [
        _make_hit("a", text="sparse text", file_name="sparse.pdf", method="sparse")
    ]

    service = RRFusionService()
    fused = service.fuse(dense_hits=dense, sparse_hits=sparse)

    assert fused[0].text == "dense text"
    assert fused[0].file_name == "dense.pdf"
