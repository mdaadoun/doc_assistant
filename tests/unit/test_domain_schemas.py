"""Unit tests for domain schemas: Chunk, Retrieval, and Chat models."""

import pytest
from pydantic import ValidationError

from models.chat import ChatRequest, ChatResponse, Citation, FinOpsMetadata
from models.chunk import ChunkDocument, ChunkMetadata
from models.retrieval import DebugRetrievalHit, DebugRetrievalResponse, RetrievalResult


def test_chunk_metadata_and_document_creation() -> None:
    """Verify ChunkMetadata and ChunkDocument instantiate and serialize correctly."""
    meta = ChunkMetadata(
        source_format="pdf",
        chunk_index=0,
        total_chunks=3,
        char_count=150,
        token_count=35,
    )
    doc = ChunkDocument(
        chunk_id="chunk-001",
        text="Sample doc chunk text.",
        file_name="guide.pdf",
        page_number=1,
        metadata=meta,
    )

    assert doc.chunk_id == "chunk-001"
    assert doc.metadata.source_format == "pdf"
    assert doc.to_dict()["metadata"]["token_count"] == 35

    restored = ChunkDocument.from_dict(doc.to_dict())
    assert restored == doc


def test_retrieval_result_and_debug_response() -> None:
    """Verify RetrievalResult and DebugRetrievalResponse functionality."""
    res = RetrievalResult(
        chunk_id="chunk-001",
        text="Retrieved content",
        file_name="guide.pdf",
        page_number=2,
        relevance_score=0.88,
        retrieval_method="dense",
    )
    dense_hit = DebugRetrievalHit(
        chunk_id="chunk-001", score=0.88, rank=1, method="dense"
    )
    rrf_hit = DebugRetrievalHit(
        chunk_id="chunk-001", score=0.0327, rank=1, method="rrf"
    )
    debug = DebugRetrievalResponse(
        query="what is rag?",
        dense_hits=[dense_hit],
        sparse_hits=[],
        rrf_fused=[rrf_hit],
        final_reranked=[res],
    )

    assert debug.query == "what is rag?"
    assert len(debug.dense_hits) == 1
    assert debug.dense_hits[0].score == 0.88
    assert debug.rrf_fused[0].method == "rrf"
    assert DebugRetrievalResponse.from_dict(debug.to_dict()) == debug


def test_chat_schemas_instantiation_and_validation() -> None:
    """Verify ChatRequest, Citation, FinOpsMetadata, and ChatResponse validation."""
    req = ChatRequest(query="How to split docs?", conversation_id="conv-101", top_k=3)
    assert req.top_k == 3

    cit = Citation(
        file_name="doc.pdf",
        page_number=5,
        chunk_id="c-5",
        excerpt="doc split logic",
        relevance_score=0.92,
    )
    finops = FinOpsMetadata(
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150,
        estimated_cost_usd=0.0003,
        execution_time_seconds=0.45,
        is_cached=False,
    )
    resp = ChatResponse(
        answer="Splitting is done recursively.",
        citations=[cit],
        confidence_score=0.95,
        grounded=True,
        latency_ms=450,
        finops=finops,
    )

    assert resp.grounded is True
    assert resp.citations[0].chunk_id == "c-5"
    assert resp.finops.total_tokens == 150
    assert ChatResponse.from_dict(resp.to_dict()) == resp


def test_schema_validation_errors() -> None:
    """Verify invalid parameter values raise ValidationError."""
    with pytest.raises(ValidationError):
        ChunkMetadata(
            source_format="pdf",
            chunk_index=-1,  # ge=0
            total_chunks=0,
            char_count=10,
            token_count=2,
        )

    with pytest.raises(ValidationError):
        ChatRequest(query="", conversation_id="conv-1")  # min_length=1

    with pytest.raises(ValidationError):
        ChatResponse(
            answer="Ans",
            citations=[],
            confidence_score=1.5,  # le=1.0
            grounded=True,
            latency_ms=100,
            finops=FinOpsMetadata(
                prompt_tokens=1,
                completion_tokens=1,
                total_tokens=2,
                estimated_cost_usd=0.0,
                execution_time_seconds=0.1,
            ),
        )
