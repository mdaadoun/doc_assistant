"""Retrieval domain models for RAG search hits and pipeline debugging."""

from pydantic import Field

from models.base import BaseDomainModel


class RetrievalResult(BaseDomainModel):
    """Retrieved search hit schema with relevance scoring."""

    chunk_id: str = Field(..., description="Unique chunk identifier")
    text: str = Field(..., description="Retrieved text snippet")
    file_name: str = Field(..., description="Source document file name")
    page_number: int = Field(..., ge=1, description="1-indexed page number")
    relevance_score: float = Field(..., description="Relevance or rerank score")
    retrieval_method: str = Field(
        ..., description="Retrieval strategy e.g. dense, sparse, rrf"
    )


class DebugRetrievalHit(BaseDomainModel):
    """Compact per-stage retrieval hit exposing raw score and rank."""

    chunk_id: str = Field(..., description="Unique chunk identifier")
    score: float = Field(..., description="Raw stage score (dense/sparse/RRF)")
    rank: int = Field(..., ge=1, description="1-indexed rank within stage")
    method: str = Field(..., description="Stage method: dense, sparse, or rrf")


class DebugRetrievalResponse(BaseDomainModel):
    """Debug payload exposing dense scores, sparse scores, and fused RRF ranks."""

    query: str = Field(..., description="Original user search query")
    dense_hits: list[DebugRetrievalHit] = Field(
        default_factory=list, description="Dense vector hits with raw scores"
    )
    sparse_hits: list[DebugRetrievalHit] = Field(
        default_factory=list, description="Sparse BM25 hits with raw scores"
    )
    rrf_fused: list[DebugRetrievalHit] = Field(
        default_factory=list, description="RRF fused hits with fused ranks"
    )
    final_reranked: list[RetrievalResult] = Field(
        default_factory=list, description="Final reranked hits"
    )


class ConfidenceDecision(BaseDomainModel):
    """Evaluation result from confidence guard threshold check."""

    passed: bool = Field(..., description="True if top candidate score meets cutoff threshold")
    top_score: float = Field(..., description="Highest relevance score among candidate hits")
    threshold: float = Field(..., ge=0.0, le=1.0, description="Calibrated confidence cutoff score")
    filtered_hits: list[RetrievalResult] = Field(
        default_factory=list, description="Candidate search hits meeting or exceeding threshold"
    )
    refusal_message: str = Field(..., description="Standardized refusal message if guard fails")

