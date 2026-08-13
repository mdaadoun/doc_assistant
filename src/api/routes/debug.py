"""GET /api/v1/debug/retrieval diagnostic endpoint."""

from fastapi import APIRouter, Query

from api.dependencies import DebugRetrievalBuilderDep
from models.retrieval import DebugRetrievalResponse

router = APIRouter(prefix="/api/v1/debug", tags=["Debug"])


@router.get(
    "/retrieval",
    response_model=DebugRetrievalResponse,
    summary="Retrieve diagnostic pipeline stage-wise search scores and ranks",
)
async def debug_retrieval_endpoint(
    debug_builder: DebugRetrievalBuilderDep,
    query: str = Query(..., min_length=1, description="Search query string"),
    dense_top_k: int | None = Query(default=None, ge=1, description="Dense vector top k"),
    sparse_top_k: int | None = Query(default=None, ge=1, description="Sparse BM25 top k"),
    rrf_top_k: int | None = Query(default=None, ge=1, description="RRF fused top k"),
    rerank_top_k: int | None = Query(default=None, ge=1, description="Final rerank top k"),
) -> DebugRetrievalResponse:
    """Run hybrid search debug pipeline and return stage-wise hits, scores, and ranks."""
    return debug_builder.build(
        query=query,
        dense_top_k=dense_top_k,
        sparse_top_k=sparse_top_k,
        rrf_top_k=rrf_top_k,
        rerank_top_k=rerank_top_k,
    )
