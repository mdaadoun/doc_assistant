"""BM25 sparse index manager: rank-bm25, tokenized corpus, JSON persistence."""

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import structlog
from rank_bm25 import BM25Okapi

from core.exceptions import RetrievalError
from models.chunk import ChunkDocument
from models.retrieval import RetrievalResult
from retrieval.bm25_tokenizer import tokenize, tokenize_corpus

logger = structlog.get_logger(__name__)

_INDEX_VERSION = 1


class BM25IndexManager:
    """Manage BM25Okapi sparse index over chunk corpus with JSON persistence."""

    def __init__(
        self,
        k1: float = 1.5,
        b: float = 0.75,
        epsilon: float = 0.25,
    ) -> None:
        """Initialize BM25 scoring hyperparameters and empty index state."""
        self.k1 = k1
        self.b = b
        self.epsilon = epsilon
        self._chunks: list[ChunkDocument] = []
        self._tokenized_corpus: list[list[str]] = []
        self._bm25: BM25Okapi | None = None

    @property
    def is_built(self) -> bool:
        """Return True when index contains at least one chunk."""
        return self._bm25 is not None and len(self._chunks) > 0

    @property
    def size(self) -> int:
        """Return number of indexed chunks."""
        return len(self._chunks)

    def build(self, chunks: Sequence[ChunkDocument]) -> int:
        """Build BM25 index from chunk documents and return chunk count."""
        self._chunks = list(chunks)
        self._tokenized_corpus = tokenize_corpus([c.text for c in self._chunks])
        if self._tokenized_corpus:
            self._bm25 = BM25Okapi(
                self._tokenized_corpus,
                k1=self.k1,
                b=self.b,
                epsilon=self.epsilon,
            )
        else:
            self._bm25 = None
        logger.info("bm25_index_built", chunk_count=len(self._chunks))
        return len(self._chunks)

    def search(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        """Search BM25 index and return top-k sparse RetrievalResult hits."""
        if not self.is_built:
            raise RetrievalError(
                message="BM25 index is empty; build it before searching",
                code="BM25_EMPTY_INDEX",
            )
        if top_k <= 0:
            raise RetrievalError(
                message="top_k must be a positive integer",
                code="INVALID_TOP_K",
                details={"top_k": top_k},
            )

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        try:
            assert self._bm25 is not None
            scores = self._bm25.get_scores(query_tokens)
        except Exception as exc:
            logger.error("bm25_search_failed", error=str(exc))
            raise RetrievalError(
                message="BM25 search failed",
                details={"query": query, "error": str(exc)},
            ) from exc

        ranked_indices = sorted(
            range(len(scores)), key=lambda i: scores[i], reverse=True
        )
        results: list[RetrievalResult] = []
        for idx in ranked_indices:
            if scores[idx] <= 0.0:
                break
            chunk = self._chunks[idx]
            results.append(
                RetrievalResult(
                    chunk_id=chunk.chunk_id,
                    text=chunk.text,
                    file_name=chunk.file_name,
                    page_number=chunk.page_number,
                    relevance_score=float(scores[idx]),
                    retrieval_method="sparse",
                )
            )
            if len(results) >= top_k:
                break
        return results

    def save(self, path: str | Path) -> Path:
        """Persist tokenized corpus and chunk metadata to JSON file."""
        target = Path(path)
        payload: dict[str, Any] = {
            "version": _INDEX_VERSION,
            "k1": self.k1,
            "b": self.b,
            "epsilon": self.epsilon,
            "chunks": [
                {
                    "chunk": chunk.model_dump(),
                    "tokens": tokens,
                }
                for chunk, tokens in zip(
                    self._chunks, self._tokenized_corpus, strict=True
                )
            ],
        }
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            logger.info("bm25_index_saved", path=str(target), chunks=len(self._chunks))
            return target
        except OSError as exc:
            raise RetrievalError(
                message=f"Failed to save BM25 index to {target}",
                details={"path": str(target), "error": str(exc)},
            ) from exc

    def load(self, path: str | Path) -> int:
        """Load tokenized corpus and chunk metadata from JSON and rebuild index."""
        target = Path(path)
        try:
            payload = json.loads(target.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RetrievalError(
                message=f"Failed to load BM25 index from {target}",
                details={"path": str(target), "error": str(exc)},
            ) from exc

        if payload.get("version") != _INDEX_VERSION:
            raise RetrievalError(
                message=f"Unsupported BM25 index version: {payload.get('version')}",
                code="BM25_INVALID_VERSION",
                details={"path": str(target), "version": payload.get("version")},
            )

        self.k1 = float(payload.get("k1", self.k1))
        self.b = float(payload.get("b", self.b))
        self.epsilon = float(payload.get("epsilon", self.epsilon))

        chunks: list[ChunkDocument] = []
        tokenized_corpus: list[list[str]] = []
        for item in payload.get("chunks", []):
            chunks.append(ChunkDocument.model_validate(item["chunk"]))
            tokenized_corpus.append([str(t) for t in item["tokens"]])

        self._chunks = chunks
        self._tokenized_corpus = tokenized_corpus
        if self._tokenized_corpus:
            self._bm25 = BM25Okapi(
                self._tokenized_corpus,
                k1=self.k1,
                b=self.b,
                epsilon=self.epsilon,
            )
        else:
            self._bm25 = None
        logger.info("bm25_index_loaded", path=str(target), chunks=len(self._chunks))
        return len(self._chunks)

    def clear(self) -> None:
        """Reset index state to empty."""
        self._chunks = []
        self._tokenized_corpus = []
        self._bm25 = None
