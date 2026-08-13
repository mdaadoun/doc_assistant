"""Unit tests for retrieval confidence guard and refusal response bypass."""

import pytest

from models.retrieval import RetrievalResult
from retrieval.confidence_guard import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    DEFAULT_REFUSAL_RESPONSE,
    ConfidenceGuard,
)


def _make_hit(chunk_id: str, score: float) -> RetrievalResult:
    """Helper to construct dummy RetrievalResult with given score."""
    return RetrievalResult(
        chunk_id=chunk_id,
        text=f"Sample text snippet for {chunk_id}",
        file_name="doc.pdf",
        page_number=1,
        relevance_score=score,
        retrieval_method="rerank",
    )


def test_confidence_guard_init_defaults() -> None:
    """Verify ConfidenceGuard initializes with default settings threshold and message."""
    guard = ConfidenceGuard()
    assert guard.threshold == DEFAULT_CONFIDENCE_THRESHOLD
    assert guard.threshold == 0.35
    assert guard.refusal_message == DEFAULT_REFUSAL_RESPONSE


def test_confidence_guard_init_custom() -> None:
    """Verify ConfidenceGuard accepts custom threshold and custom refusal message."""
    custom_msg = "Custom refusal: No document support."
    guard = ConfidenceGuard(threshold=0.5, refusal_message=custom_msg)
    assert guard.threshold == 0.5
    assert guard.refusal_message == custom_msg


def test_confidence_guard_init_clamping() -> None:
    """Verify ConfidenceGuard clamps threshold values to [0.0, 1.0]."""
    guard_high = ConfidenceGuard(threshold=1.5)
    assert guard_high.threshold == 1.0

    guard_low = ConfidenceGuard(threshold=-0.2)
    assert guard_low.threshold == 0.0


def test_confidence_guard_is_confident_empty_hits() -> None:
    """Verify is_confident returns False for empty hit list."""
    guard = ConfidenceGuard()
    assert not guard.is_confident([])


def test_confidence_guard_is_confident_below_threshold() -> None:
    """Verify is_confident returns False when top score is strictly below S_min (0.35)."""
    guard = ConfidenceGuard(threshold=0.35)
    hits = [_make_hit("c1", 0.349), _make_hit("c2", 0.12)]
    assert not guard.is_confident(hits)


def test_confidence_guard_is_confident_exact_threshold() -> None:
    """Verify is_confident returns True when top score equals S_min cutoff (0.35)."""
    guard = ConfidenceGuard(threshold=0.35)
    hits = [_make_hit("c1", 0.35), _make_hit("c2", 0.20)]
    assert guard.is_confident(hits)


def test_confidence_guard_is_confident_above_threshold() -> None:
    """Verify is_confident returns True when top score exceeds S_min (0.35)."""
    guard = ConfidenceGuard(threshold=0.35)
    hits = [_make_hit("c1", 0.88), _make_hit("c2", 0.40)]
    assert guard.is_confident(hits)


def test_confidence_guard_filter_hits() -> None:
    """Verify filter_hits preserves only candidates meeting or exceeding threshold."""
    guard = ConfidenceGuard(threshold=0.35)
    hits = [
        _make_hit("c1", 0.85),
        _make_hit("c2", 0.349),
        _make_hit("c3", 0.35),
        _make_hit("c4", 0.10),
    ]
    filtered = guard.filter_hits(hits)
    assert len(filtered) == 2
    assert [h.chunk_id for h in filtered] == ["c1", "c3"]


def test_confidence_guard_evaluate_passed() -> None:
    """Verify evaluate returns structured decision for passing retrieval hits."""
    guard = ConfidenceGuard(threshold=0.35)
    hits = [_make_hit("c1", 0.75), _make_hit("c2", 0.20)]
    decision = guard.evaluate(hits)

    assert decision.passed is True
    assert decision.top_score == 0.75
    assert decision.threshold == 0.35
    assert len(decision.filtered_hits) == 1
    assert decision.filtered_hits[0].chunk_id == "c1"
    assert decision.refusal_message == DEFAULT_REFUSAL_RESPONSE


def test_confidence_guard_evaluate_failed() -> None:
    """Verify evaluate returns failed decision with empty filtered_hits for low confidence."""
    guard = ConfidenceGuard(threshold=0.35)
    hits = [_make_hit("c1", 0.25), _make_hit("c2", 0.10)]
    decision = guard.evaluate(hits)

    assert decision.passed is False
    assert decision.top_score == 0.25
    assert decision.threshold == 0.35
    assert decision.filtered_hits == []
    assert decision.refusal_message == DEFAULT_REFUSAL_RESPONSE


def test_confidence_guard_create_refusal_response() -> None:
    """Verify create_refusal_response constructs valid ChatResponse refusal payload."""
    guard = ConfidenceGuard()
    response = guard.create_refusal_response(top_score=0.20, latency_ms=150)

    assert response.answer == DEFAULT_REFUSAL_RESPONSE
    assert response.citations == []
    assert response.confidence_score == 0.20
    assert response.grounded is False
    assert response.latency_ms == 150
    assert response.finops.prompt_tokens == 0
    assert response.finops.completion_tokens == 0
    assert response.finops.total_tokens == 0
    assert response.finops.estimated_cost_usd == 0.0
    assert response.finops.execution_time_seconds == 0.15
    assert response.finops.is_cached is False


def test_confidence_guard_create_refusal_response_clamping() -> None:
    """Verify confidence score clamping in create_refusal_response."""
    guard = ConfidenceGuard()
    resp_negative = guard.create_refusal_response(top_score=-0.5, latency_ms=0)
    assert resp_negative.confidence_score == 0.0

    resp_excess = guard.create_refusal_response(top_score=1.5, latency_ms=0)
    assert resp_excess.confidence_score == 1.0
