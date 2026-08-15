"""Chat pipeline service orchestrating hybrid retrieval, confidence gating, and SSE streaming generation."""

from collections.abc import AsyncGenerator
from typing import Any

import structlog

from generation.engine import GroundedGenerator
from generation.sse import SSEResponseHandler
from models.chat import ChatRequest, Citation
from retrieval.confidence_guard import ConfidenceGuard
from retrieval.dense_search import DenseSearchService
from retrieval.reranker_service import RerankerService
from retrieval.rrf_fusion import RRFusionService
from retrieval.sparse_search import SparseSearchService

logger = structlog.get_logger(__name__)


class ChatService:
    """Service layer orchestrating RAG chat pipeline and SSE token stream generation."""

    def __init__(
        self,
        dense_search: DenseSearchService | None = None,
        sparse_search: SparseSearchService | None = None,
        rrf_fusion: RRFusionService | None = None,
        reranker: RerankerService | None = None,
        confidence_guard: ConfidenceGuard | None = None,
        grounded_generator: GroundedGenerator | None = None,
        sse_handler: SSEResponseHandler | None = None,
    ) -> None:
        """Initialize chat pipeline service dependencies."""
        self.dense_search = dense_search
        self.sparse_search = sparse_search
        self.rrf_fusion = rrf_fusion
        self.reranker = reranker
        self.confidence_guard = confidence_guard or ConfidenceGuard()
        self.grounded_generator = grounded_generator
        self.sse_handler = sse_handler or SSEResponseHandler()

    async def _async_refusal_stream(self, message: str) -> AsyncGenerator[str, None]:
        """Yield refusal message as single token delta stream."""
        yield message

    async def stream_chat(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """Execute hybrid search, confidence check, generation, and yield SSE formatted events."""
        logger.info(
            "chat_stream_requested",
            conversation_id=request.conversation_id,
            query=request.query,
            top_k=request.top_k,
        )

        candidates: list[Any] = []

        if self.dense_search and self.sparse_search and self.rrf_fusion:
            dense_hits = self.dense_search.search(request.query)
            sparse_hits = self.sparse_search.search(request.query)
            fused = self.rrf_fusion.fuse(dense_hits=dense_hits, sparse_hits=sparse_hits)
            if self.reranker:
                candidates = self.reranker.rerank(
                    query=request.query, hits=fused, top_k=request.top_k
                )
            else:
                candidates = list(fused[: request.top_k])

        decision = self.confidence_guard.evaluate(candidates)

        if not decision.passed:
            logger.info(
                "chat_stream_refused",
                conversation_id=request.conversation_id,
                top_score=decision.top_score,
            )
            token_gen = self._async_refusal_stream(decision.refusal_message)
            async for frame in self.sse_handler.stream_generator(
                token_stream=token_gen,
                conversation_id=request.conversation_id,
                confidence_score=decision.top_score,
                grounded=False,
                citations=[],
            ):
                yield frame
            return

        citations = [
            Citation(
                file_name=hit.file_name,
                page_number=hit.page_number,
                chunk_id=hit.chunk_id,
                excerpt=hit.text,
                relevance_score=hit.relevance_score,
            )
            for hit in decision.filtered_hits
        ]

        if self.grounded_generator is None:
            token_gen = self._async_refusal_stream("Generator service unavailable.")
        else:
            token_gen = self.grounded_generator.generate_stream(
                query=request.query, contexts=decision.filtered_hits
            )

        async for frame in self.sse_handler.stream_generator(
            token_stream=token_gen,
            conversation_id=request.conversation_id,
            confidence_score=decision.top_score,
            grounded=True,
            citations=citations,
        ):
            yield frame
