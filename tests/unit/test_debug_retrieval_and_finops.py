"""Unit tests for DebugRetrievalResponse, DebugRetrievalHit, and FinOpsMetadata."""

import pytest
from pydantic import ValidationError

from models.chat import FinOpsMetadata
from models.retrieval import DebugRetrievalHit, DebugRetrievalResponse, RetrievalResult


def test_debug_retrieval_hit_validation() -> None:
    """Verify DebugRetrievalHit enforces rank >= 1 and immutability."""
    hit = DebugRetrievalHit(chunk_id="chk-1", score=0.9, rank=1, method="dense")
    assert hit.chunk_id == "chk-1"
    assert hit.score == 0.9
    assert hit.rank == 1
    assert hit.method == "dense"

    with pytest.raises(ValidationError):
        DebugRetrievalHit(chunk_id="chk-1", score=0.9, rank=0, method="dense")

    with pytest.raises(ValidationError):
        hit.rank = 2


def test_debug_retrieval_response_defaults_and_serialization() -> None:
    """Verify DebugRetrievalResponse handles default empty lists and roundtrip serialization."""
    debug_empty = DebugRetrievalResponse(query="test query")
    assert debug_empty.query == "test query"
    assert debug_empty.dense_hits == []
    assert debug_empty.sparse_hits == []
    assert debug_empty.rrf_fused == []
    assert debug_empty.final_reranked == []

    dense_hit = DebugRetrievalHit(chunk_id="chk-10", score=0.95, rank=1, method="dense")
    sparse_hit = DebugRetrievalHit(
        chunk_id="chk-11", score=14.8, rank=1, method="sparse"
    )
    rrf_hit = DebugRetrievalHit(chunk_id="chk-10", score=0.0327, rank=1, method="rrf")
    reranked = RetrievalResult(
        chunk_id="chk-10",
        text="Sample context hit",
        file_name="specs.pdf",
        page_number=1,
        relevance_score=0.892,
        retrieval_method="rerank",
    )
    debug_populated = DebugRetrievalResponse(
        query="hybrid search test",
        dense_hits=[dense_hit],
        sparse_hits=[sparse_hit],
        rrf_fused=[rrf_hit],
        final_reranked=[reranked],
    )

    dict_repr = debug_populated.to_dict()
    assert dict_repr["query"] == "hybrid search test"
    assert len(dict_repr["dense_hits"]) == 1
    assert dict_repr["dense_hits"][0]["chunk_id"] == "chk-10"
    assert dict_repr["dense_hits"][0]["rank"] == 1
    assert dict_repr["sparse_hits"][0]["score"] == 14.8
    assert dict_repr["rrf_fused"][0]["method"] == "rrf"

    restored = DebugRetrievalResponse.from_dict(dict_repr)
    assert restored == debug_populated


def test_debug_retrieval_response_immutability_and_validation() -> None:
    """Verify DebugRetrievalResponse immutability (frozen) and type validation."""
    debug = DebugRetrievalResponse(query="immutable test")
    with pytest.raises(ValidationError):
        debug.query = "new query"

    with pytest.raises(ValidationError):
        DebugRetrievalResponse.from_dict({})


def test_finops_metadata_instantiation_and_defaults() -> None:
    """Verify FinOpsMetadata field constraints and default values."""
    finops = FinOpsMetadata(
        prompt_tokens=250,
        completion_tokens=100,
        total_tokens=350,
        estimated_cost_usd=0.0012,
        execution_time_seconds=0.35,
    )
    assert finops.is_cached is False
    assert finops.prompt_tokens == 250
    assert finops.estimated_cost_usd == 0.0012

    cached_finops = FinOpsMetadata(
        prompt_tokens=250,
        completion_tokens=0,
        total_tokens=250,
        estimated_cost_usd=0.0,
        execution_time_seconds=0.01,
        is_cached=True,
    )
    assert cached_finops.is_cached is True
    assert FinOpsMetadata.from_dict(cached_finops.to_dict()) == cached_finops


def test_finops_metadata_validation_boundaries() -> None:
    """Verify FinOpsMetadata raises ValidationError on negative metrics."""
    with pytest.raises(ValidationError):
        FinOpsMetadata(
            prompt_tokens=-1,
            completion_tokens=10,
            total_tokens=10,
            estimated_cost_usd=0.01,
            execution_time_seconds=0.1,
        )

    with pytest.raises(ValidationError):
        FinOpsMetadata(
            prompt_tokens=10,
            completion_tokens=10,
            total_tokens=20,
            estimated_cost_usd=-0.001,
            execution_time_seconds=0.1,
        )

    with pytest.raises(ValidationError):
        FinOpsMetadata(
            prompt_tokens=10,
            completion_tokens=10,
            total_tokens=20,
            estimated_cost_usd=0.001,
            execution_time_seconds=-0.5,
        )
