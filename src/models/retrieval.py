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
    retrieval_method: str = Field(..., description="Retrieval strategy e.g. dense, sparse, rrf")


class DebugRetrievalResponse(BaseDomainModel):
    """Debug payload capturing retrieval pipeline stage outputs."""

    query: str = Field(..., description="Original user search query")
    dense_hits: list[RetrievalResult] = Field(default_factory=list, description="Dense vector hits")
    sparse_hits: list[RetrievalResult] = Field(default_factory=list, description="Sparse BM25 hits")
    rrf_fused: list[RetrievalResult] = Field(default_factory=list, description="RRF fused hits")
    final_reranked: list[RetrievalResult] = Field(default_factory=list, description="Final reranked hits")
