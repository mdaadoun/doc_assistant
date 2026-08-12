"""Indexing orchestrator: embed chunks, upsert vectors, build BM25 index."""

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import structlog

from clients.base_embedding import BaseEmbeddingAdapter
from core.exceptions import RetrievalError
from models.chunk import ChunkDocument
from retrieval.bm25_index import BM25IndexManager
from retrieval.vector_store import VectorStoreAdapter

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class IndexingResult:
    """Summary of a completed indexing operation."""

    chunk_count: int
    vector_count: int
    bm25_count: int
    collection_name: str
    bm25_path: Path | None = None


class IndexingOrchestrator:
    """Coordinate embedding, vector upsert, and BM25 index build for chunks."""

    def __init__(
        self,
        embedding_adapter: BaseEmbeddingAdapter,
        vector_store: VectorStoreAdapter,
        bm25_index: BM25IndexManager | None = None,
        batch_size: int = 100,
    ) -> None:
        """Initialize orchestrator with embedding, vector store, and BM25 components."""
        self.embedding_adapter = embedding_adapter
        self.vector_store = vector_store
        self.bm25_index = bm25_index or BM25IndexManager()
        self.batch_size = max(1, batch_size)

    def index_chunks(
        self,
        chunks: Sequence[ChunkDocument],
        collection_name: str | None = None,
        bm25_path: str | Path | None = None,
    ) -> IndexingResult:
        """Embed chunks, upsert vectors into Qdrant, and build BM25 index."""
        chunk_list = list(chunks)
        target_collection = collection_name or self.vector_store.collection_name

        if not chunk_list:
            logger.info("indexing_skipped_empty_chunks")
            return IndexingResult(
                chunk_count=0,
                vector_count=0,
                bm25_count=0,
                collection_name=target_collection,
            )

        texts = [c.text for c in chunk_list]
        embeddings = self.embedding_adapter.embed_batch(
            texts, batch_size=self.batch_size
        )

        if len(embeddings) != len(chunk_list):
            raise RetrievalError(
                message="Embedding count mismatch after batch embedding",
                code="EMBEDDING_COUNT_MISMATCH",
                details={
                    "chunks_count": len(chunk_list),
                    "embeddings_count": len(embeddings),
                },
            )

        self._validate_dimension(embeddings)

        self.vector_store.ensure_collection(collection_name=collection_name)
        vector_count = self.vector_store.upsert_chunks(
            chunks=chunk_list,
            embeddings=embeddings,
            collection_name=collection_name,
        )

        bm25_count = self.bm25_index.build(chunk_list)

        saved_path: Path | None = None
        if bm25_path is not None:
            saved_path = self.bm25_index.save(bm25_path)

        logger.info(
            "indexing_completed",
            chunks=len(chunk_list),
            vectors=vector_count,
            bm25=bm25_count,
            collection=target_collection,
        )
        return IndexingResult(
            chunk_count=len(chunk_list),
            vector_count=vector_count,
            bm25_count=bm25_count,
            collection_name=target_collection,
            bm25_path=saved_path,
        )

    def _validate_dimension(self, embeddings: Sequence[Sequence[float]]) -> None:
        """Ensure every embedding vector matches vector store dimension."""
        expected = self.vector_store.vector_dim
        for idx, vec in enumerate(embeddings):
            if len(vec) != expected:
                raise RetrievalError(
                    message="Embedding dimension mismatch with vector store",
                    code="EMBEDDING_DIM_MISMATCH",
                    details={
                        "index": idx,
                        "embedding_dim": len(vec),
                        "expected_dim": expected,
                    },
                )