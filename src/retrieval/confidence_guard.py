"""Confidence guard gating mechanism for anti-hallucination context filtering."""

from collections.abc import Sequence

import structlog

from core.config import get_settings
from models.chat import ChatResponse, FinOpsMetadata
from models.retrieval import ConfidenceDecision, RetrievalResult

logger = structlog.get_logger(__name__)

DEFAULT_REFUSAL_RESPONSE: str = (
    "I cannot answer this question based on the available documentation."
)
DEFAULT_CONFIDENCE_THRESHOLD: float = 0.35


class ConfidenceGuard:
    """Evaluates cross-encoder retrieval confidence against minimum score threshold S_min."""

    def __init__(
        self,
        threshold: float | None = None,
        refusal_message: str | None = None,
    ) -> None:
        """Initialize guard with configured threshold cutoff and refusal message."""
        settings = get_settings()
        raw_threshold = (
            threshold if threshold is not None else settings.confidence_threshold
        )
        self.threshold: float = max(0.0, min(1.0, float(raw_threshold)))
        self.refusal_message: str = refusal_message or DEFAULT_REFUSAL_RESPONSE

    def is_confident(self, hits: Sequence[RetrievalResult]) -> bool:
        """Check if top candidate hit meets or exceeds S_min cutoff score."""
        if not hits:
            return False
        return max(hit.relevance_score for hit in hits) >= self.threshold

    def filter_hits(
        self, hits: Sequence[RetrievalResult]
    ) -> list[RetrievalResult]:
        """Filter candidates keeping only hits with relevance_score >= S_min."""
        return [hit for hit in hits if hit.relevance_score >= self.threshold]

    def evaluate(self, hits: Sequence[RetrievalResult]) -> ConfidenceDecision:
        """Evaluate candidate hits and return structured confidence decision."""
        top_score = max((hit.relevance_score for hit in hits), default=0.0)
        passed = self.is_confident(hits)
        filtered = self.filter_hits(hits) if passed else []

        logger.info(
            "confidence_guard_evaluated",
            top_score=top_score,
            threshold=self.threshold,
            passed=passed,
            input_hits=len(hits),
            filtered_hits=len(filtered),
        )

        return ConfidenceDecision(
            passed=passed,
            top_score=top_score,
            threshold=self.threshold,
            filtered_hits=filtered,
            refusal_message=self.refusal_message,
        )

    def create_refusal_response(
        self,
        top_score: float = 0.0,
        latency_ms: int = 0,
    ) -> ChatResponse:
        """Construct standard ungrounded refusal ChatResponse payload."""
        clamped_score = max(0.0, min(1.0, float(top_score)))
        latency = max(0, int(latency_ms))
        sec = latency / 1000.0

        return ChatResponse(
            answer=self.refusal_message,
            citations=[],
            confidence_score=clamped_score,
            grounded=False,
            latency_ms=latency,
            finops=FinOpsMetadata(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                estimated_cost_usd=0.0,
                execution_time_seconds=sec,
                is_cached=False,
            ),
        )
