"""Vector store adapter for Qdrant embedding indexing and dense retrieval."""

import uuid
from collections.abc import Sequence
from typing import Any

import structlog
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from qdrant_client.models import Distance, PointIdsList, PointStruct, VectorParams

from core.config import get_settings
from core.exceptions import RetrievalError
from models.chunk import ChunkDocument
from models.retrieval import RetrievalResult

logger = structlog.get_logger(__name__)


def _to_valid_uuid(id_str: str) -> str:
    """Convert arbitrary string identifier to valid Qdrant UUID string."""
    try:
        uuid.UUID(id_str)
        return id_str
    except ValueError:
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, id_str))


class VectorStoreAdapter:
    """Adapter encapsulating Qdrant vector database operations."""

    def __init__(
        self,
        client: QdrantClient | None = None,
        host: str | None = None,
        port: int | None = None,
        collection_name: str | None = None,
        vector_dim: int = 1536,
        distance: Distance = Distance.COSINE,
    ) -> None:
        """Initialize Qdrant vector store adapter configuration and client connection."""
        settings = get_settings()
        self.host = host or settings.qdrant_host
        self.port = port or settings.qdrant_port
        self.collection_name = collection_name or settings.qdrant_collection
        self.vector_dim = vector_dim
        self.distance = distance

        try:
            if client is not None:
                self.client = client
            else:
                self.client = QdrantClient(host=self.host, port=self.port)
        except Exception as exc:
            logger.error("qdrant_client_init_failed", host=self.host, error=str(exc))
            raise RetrievalError(
                message=f"Failed to initialize Qdrant client at {self.host}:{self.port}",
                details={"host": self.host, "port": self.port, "error": str(exc)},
            ) from exc

    def collection_exists(self, collection_name: str | None = None) -> bool:
        """Check if vector collection exists in Qdrant."""
        target = collection_name or self.collection_name
        try:
            return bool(self.client.collection_exists(collection_name=target))
        except Exception as exc:
            raise RetrievalError(
                message=f"Failed to check collection existence for {target}",
                details={"collection_name": target, "error": str(exc)},
            ) from exc

    def ensure_collection(
        self,
        collection_name: str | None = None,
        vector_dim: int | None = None,
        distance: Distance | None = None,
        recreate: bool = False,
    ) -> bool:
        """Create vector collection if missing or when recreation is requested."""
        target = collection_name or self.collection_name
        dim = vector_dim or self.vector_dim
        dist = distance or self.distance

        try:
            if recreate and self.collection_exists(target):
                self.client.delete_collection(collection_name=target)

            if not self.collection_exists(target):
                self.client.create_collection(
                    collection_name=target,
                    vectors_config=VectorParams(size=dim, distance=dist),
                )
                logger.info("qdrant_collection_created", name=target, dim=dim)
            return True
        except Exception as exc:
            logger.error("qdrant_collection_create_failed", name=target, error=str(exc))
            raise RetrievalError(
                message=f"Failed to ensure vector collection {target}",
                details={"collection_name": target, "dim": dim, "error": str(exc)},
            ) from exc

    def upsert_chunks(
        self,
        chunks: Sequence[ChunkDocument],
        embeddings: Sequence[list[float]],
        collection_name: str | None = None,
        batch_size: int = 512,
    ) -> int:
        """Upsert chunk documents and dense vectors in batches into Qdrant."""
        if len(chunks) != len(embeddings):
            raise RetrievalError(
                message="Mismatch between chunk count and embedding count",
                details={
                    "chunks_count": len(chunks),
                    "embeddings_count": len(embeddings),
                },
            )

        target = collection_name or self.collection_name
        points: list[PointStruct] = []
        for chunk, embedding in zip(chunks, embeddings, strict=True):
            payload = {
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "file_name": chunk.file_name,
                "page_number": chunk.page_number,
                "source_format": chunk.metadata.source_format,
                "chunk_index": chunk.metadata.chunk_index,
                "total_chunks": chunk.metadata.total_chunks,
            }
            points.append(
                PointStruct(
                    id=_to_valid_uuid(chunk.chunk_id),
                    vector=embedding,
                    payload=payload,
                )
            )

        try:
            total = 0
            for i in range(0, len(points), batch_size):
                batch = points[i : i + batch_size]
                self.client.upsert(collection_name=target, points=batch)
                total += len(batch)
            logger.info("qdrant_upsert_success", count=total, collection=target)
            return total
        except Exception as exc:
            logger.error("qdrant_upsert_failed", collection=target, error=str(exc))
            raise RetrievalError(
                message=f"Failed to upsert vectors into collection {target}",
                details={
                    "collection_name": target,
                    "count": len(points),
                    "error": str(exc),
                },
            ) from exc

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        collection_name: str | None = None,
        filter_criteria: dict[str, Any] | None = None,
    ) -> list[RetrievalResult]:
        """Execute dense vector similarity search returning RetrievalResult objects."""
        target = collection_name or self.collection_name
        try:
            query_filter: qmodels.Filter | None = None
            if filter_criteria:
                must_conditions: list[Any] = [
                    qmodels.FieldCondition(key=k, match=qmodels.MatchValue(value=v))
                    for k, v in filter_criteria.items()
                ]
                query_filter = qmodels.Filter(must=must_conditions)

            res = self.client.query_points(
                collection_name=target,
                query=query_vector,
                limit=top_k,
                query_filter=query_filter,
            )

            results: list[RetrievalResult] = []
            for point in res.points:
                payload = point.payload or {}
                results.append(
                    RetrievalResult(
                        chunk_id=str(payload.get("chunk_id", point.id)),
                        text=str(payload.get("text", "")),
                        file_name=str(payload.get("file_name", "")),
                        page_number=int(payload.get("page_number", 1)),
                        relevance_score=float(point.score),
                        retrieval_method="dense",
                    )
                )
            return results
        except Exception as exc:
            logger.error("qdrant_search_failed", collection=target, error=str(exc))
            raise RetrievalError(
                message=f"Dense vector search failed on collection {target}",
                details={"collection_name": target, "error": str(exc)},
            ) from exc

    def get_count(self, collection_name: str | None = None) -> int:
        """Return total point count in target Qdrant collection."""
        target = collection_name or self.collection_name
        try:
            res = self.client.count(collection_name=target)
            return int(res.count)
        except Exception as exc:
            raise RetrievalError(
                message=f"Failed to fetch point count for collection {target}",
                details={"collection_name": target, "error": str(exc)},
            ) from exc

    def delete_points(
        self,
        point_ids: Sequence[str],
        collection_name: str | None = None,
    ) -> bool:
        """Delete points by their chunk identifiers."""
        target = collection_name or self.collection_name
        if not point_ids:
            return True
        uuid_ids: list[Any] = [_to_valid_uuid(pid) for pid in point_ids]
        try:
            self.client.delete(
                collection_name=target,
                points_selector=PointIdsList(points=uuid_ids),
            )
            return True
        except Exception as exc:
            raise RetrievalError(
                message=f"Failed to delete points from collection {target}",
                details={"collection_name": target, "error": str(exc)},
            ) from exc

    def delete_collection(self, collection_name: str | None = None) -> bool:
        """Delete Qdrant collection if present."""
        target = collection_name or self.collection_name
        try:
            if self.collection_exists(target):
                self.client.delete_collection(collection_name=target)
                logger.info("qdrant_collection_deleted", name=target)
                return True
            return False
        except Exception as exc:
            raise RetrievalError(
                message=f"Failed to delete collection {target}",
                details={"collection_name": target, "error": str(exc)},
            ) from exc
