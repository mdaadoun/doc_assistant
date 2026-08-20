"""Unit tests for pure retrieval metrics, latency percentiles, and report formatting."""

from pathlib import Path
from unittest.mock import patch

import pytest

from core.exceptions import EvaluationError
from models.evaluation import (
    EvalDatasetItem,
    EvalGroundTruthCitation,
    RetrievalBenchmarkReport,
    RetrievalMetricThresholds,
    RetrievalQueryResult,
)
from models.retrieval import RetrievalResult
from retrieval.metrics import (
    compute_hit_at_k,
    compute_latency_statistics,
    compute_percentile,
    compute_precision_at_k,
    compute_recall_at_k,
    compute_reciprocal_rank,
    match_retrieved_chunks,
)
from retrieval.report_formatter import (
    format_retrieval_markdown_report,
    write_retrieval_markdown_report,
)


def test_compute_precision_at_k_various_cases() -> None:
    """Verify precision@k calculation under normal and boundary conditions."""
    assert compute_precision_at_k([], ["c1"], k=5) == 0.0
    assert compute_precision_at_k(["c1"], [], k=5) == 0.0
    assert compute_precision_at_k(["c1", "c2"], ["c1"], k=0) == 0.0
    assert compute_precision_at_k(["c1", "c2", "c3"], ["c1", "c3"], k=2) == 0.5
    assert compute_precision_at_k(["c1", "c2"], ["c1", "c2"], k=2) == 1.0
    assert (
        compute_precision_at_k(["c1", "c2", "c3", "c4", "c5"], ["c1", "c2"], k=5) == 0.4
    )


def test_compute_recall_at_k_various_cases() -> None:
    """Verify recall@k calculation under normal and boundary conditions."""
    assert compute_recall_at_k([], [], k=5) == 1.0
    assert compute_recall_at_k(["c1"], [], k=5) == 0.0
    assert compute_recall_at_k([], ["c1"], k=5) == 0.0
    assert compute_recall_at_k(["c1", "c2"], ["c1", "c2", "c3", "c4"], k=2) == 0.5
    assert compute_recall_at_k(["c1", "c2", "c3"], ["c1"], k=3) == 1.0


def test_compute_reciprocal_rank_and_hit_at_k() -> None:
    """Verify MRR reciprocal rank and hit@k calculations."""
    assert compute_reciprocal_rank([], ["c1"], k=5) == 0.0
    assert compute_reciprocal_rank(["c1", "c2"], [], k=5) == 0.0
    assert compute_reciprocal_rank(["c1", "c2"], ["c1"], k=5) == 1.0
    assert compute_reciprocal_rank(["c2", "c1"], ["c1"], k=5) == 0.5
    assert compute_reciprocal_rank(["c2", "c3", "c1"], ["c1"], k=5) == pytest.approx(
        1.0 / 3.0
    )
    assert compute_reciprocal_rank(["c2", "c3", "c4"], ["c1"], k=3) == 0.0

    assert compute_hit_at_k([], ["c1"], k=5) is False
    assert compute_hit_at_k(["c1"], [], k=5) is False
    assert compute_hit_at_k(["c1", "c2"], ["c2"], k=2) is True
    assert compute_hit_at_k(["c1", "c2"], ["c3"], k=2) is False


def test_match_retrieved_chunks() -> None:
    """Verify matching chunks by chunk ID and by (file_name, page_number)."""
    item = EvalDatasetItem(
        query_id="q1",
        query="What is the SLA?",
        ground_truth_answer="30 days notice.",
        ground_truth_citations=[
            EvalGroundTruthCitation(
                file_name="sla.pdf", page_number=2, chunk_id="chunk_sla_1"
            ),
            EvalGroundTruthCitation(
                file_name="legal.pdf", page_number=5, chunk_id="chunk_leg_1"
            ),
        ],
    )
    hits = [
        RetrievalResult(
            chunk_id="chunk_sla_1",
            text="t1",
            file_name="sla.pdf",
            page_number=2,
            relevance_score=0.9,
            retrieval_method="hybrid",
        ),
        RetrievalResult(
            chunk_id="chunk_diff_id",
            text="t2",
            file_name="legal.pdf",
            page_number=5,
            relevance_score=0.8,
            retrieval_method="hybrid",
        ),
        RetrievalResult(
            chunk_id="chunk_unrelated",
            text="t3",
            file_name="other.pdf",
            page_number=1,
            relevance_score=0.2,
            retrieval_method="hybrid",
        ),
    ]
    matched = match_retrieved_chunks(hits, item)
    assert matched == ["chunk_sla_1", "chunk_diff_id"]


def test_compute_percentile_and_latency_statistics() -> None:
    """Verify percentile computation and full latency statistics dictionary."""
    assert compute_percentile([], 50.0) == 0.0
    assert compute_percentile([10.0], 90.0) == 10.0
    data = [10.0, 20.0, 30.0, 40.0, 50.0]
    assert compute_percentile(data, 50.0) == 30.0
    assert compute_percentile(data, 0.0) == 10.0
    assert compute_percentile(data, 100.0) == 50.0

    empty_stats = compute_latency_statistics([])
    assert empty_stats["p50_ms"] == 0.0

    stats = compute_latency_statistics([100.0, 200.0, 300.0, 400.0, 500.0])
    assert stats["p50_ms"] == 300.0
    assert stats["mean_ms"] == 300.0
    assert stats["max_ms"] == 500.0
    assert stats["p95_ms"] > 400.0


def test_format_and_write_markdown_report(tmp_path: Path) -> None:
    """Verify report formatting and disk persistence."""
    q_in = RetrievalQueryResult(
        query_id="q1",
        query="Notice period?",
        category="sla",
        is_out_of_corpus=False,
        retrieved_chunk_ids=["c1"],
        ground_truth_chunk_ids=["c1"],
        top_k=5,
        precision_at_k=0.8,
        recall_at_k=1.0,
        reciprocal_rank=1.0,
        hit_at_k=True,
        passed_confidence_guard=True,
        top_score=0.88,
        is_correctly_refused=True,
        latency_ms=120.0,
    )
    q_out = RetrievalQueryResult(
        query_id="q_out_1",
        query="Alien invasion policy?",
        category="out_of_corpus",
        is_out_of_corpus=True,
        top_k=5,
        precision_at_k=0.0,
        recall_at_k=1.0,
        reciprocal_rank=0.0,
        hit_at_k=False,
        passed_confidence_guard=False,
        top_score=0.12,
        is_correctly_refused=True,
        latency_ms=45.0,
    )
    report = RetrievalBenchmarkReport(
        total_queries=2,
        in_corpus_queries=1,
        out_of_corpus_queries=1,
        mean_precision_at_k=0.8,
        mean_recall_at_k=1.0,
        mrr=1.0,
        hit_rate_at_k=1.0,
        honesty_filter_precision=1.0,
        latency_p50_ms=82.5,
        latency_p90_ms=112.5,
        latency_p95_ms=116.25,
        latency_p99_ms=119.25,
        latency_mean_ms=82.5,
        latency_max_ms=120.0,
        thresholds=RetrievalMetricThresholds(),
        precision_threshold_passed=True,
        honesty_threshold_passed=True,
        latency_threshold_passed=True,
        all_passed=True,
        query_results=[q_in, q_out],
    )

    rendered = format_retrieval_markdown_report(report)
    assert "# Retrieval & Grounding Benchmark Report" in rendered
    assert "retrieval_precision@5" in rendered
    assert "honesty_filter_precision" in rendered
    assert "✅ PASS" in rendered

    out_file = tmp_path / "reports" / "test_report.md"
    written_path = write_retrieval_markdown_report(report, out_file)
    assert written_path.is_file()
    assert written_path.read_text(encoding="utf-8") == rendered

    with patch("builtins.open", side_effect=OSError("Disk full")):
        with pytest.raises(EvaluationError) as exc_info:
            write_retrieval_markdown_report(report, out_file)
        assert exc_info.value.code == "REPORT_WRITE_ERROR"
