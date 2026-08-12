"""Dense vector search service: embed query, retrieve top-50 Qdrant hits."""

import structlog

from clients.base_embedding import BaseEmbeddingAdapter
from core.exceptions import RetrievalError
from models.retrieval import RetrievalResult
from retrieval.vector_store import VectorStoreAdapter

logger = structlog.get_logger(__name__)

DENSE_TOP_K_DEFAULT = 50


class DenseSearchService:
    """Encapsulate dense retrieval: query embedding + top-k Qdrant cosine search."""

    def __init__(
        self,
        embedding_adapter: BaseEmbeddingAdapter,
        vector_store: VectorStoreAdapter,
        top_k: int = DENSE_TOP_K_DEFAULT,
    ) -> None:
        """Configure dense search service with embedding and vector store components."""
        self.embedding_adapter = embedding_adapter
        self.vector_store = vector_store
        self.top_k = max(1, top_k)

    def search(
        self,
        query: str,
        top_k: int | None = None,
        collection_name: str | None = None,
        filter_criteria: dict[str, str] | None = None,
    ) -> list[RetrievalResult]:
        """Embed query text, run dense Qdrant search, return ranked hits."""
        if not query or not query.strip():
            raise RetrievalError(
                message="Query must be a non-empty string",
                code="EMPTY_QUERY",
            )

        target_top_k = max(1, top_k or self.top_k)

        try:
            query_vector = self.embedding_adapter.embed_text(query)
        except RetrievalError:
            raise
        except Exception as exc:
            logger.error("dense_query_embed_failed", error=str(exc))
            raise RetrievalError(
                message="Failed to embed dense search query",
                details={"query": query, "error": str(exc)},
            ) from exc

        if len(query_vector) != self.vector_store.vector_dim:
            raise RetrievalError(
                message="Query embedding dimension mismatches vector store",
                code="QUERY_DIM_MISMATCH",
                details={
                    "query_dim": len(query_vector),
                    "expected_dim": self.vector_store.vector_dim,
                },
            )

        if not self.vector_store.collection_exists(collection_name):
            raise RetrievalError(
                message="Vector collection does not exist; index data first",
                code="COLLECTION_NOT_FOUND",
                details={
                    "collection_name": collection_name or self.vector_store.collection_name
                },
            )

        results = self.vector_store.search(
            query_vector=query_vector,
            top_k=target_top_k,
            collection_name=collection_name,
            filter_criteria=filter_criteria,
        )

        logger.info(
            "dense_search_completed",
            query=query,
            top_k=target_top_k,
            hits=len(results),
        )
        return results