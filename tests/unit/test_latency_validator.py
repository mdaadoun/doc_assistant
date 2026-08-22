"""Unit tests for LatencyBenchmarkValidator verifying p95_latency <= 3000ms."""

import time
from pathlib import Path

import pytest

from core.eval_dataset import load_eval_dataset_from_jsonl
from core.exceptions import EvaluationError
from models.evaluation import (
    EvalDataset,
    EvalDatasetItem,
    EvalGroundTruthCitation,
)
from models.latency import (
    LatencyMetricThresholds,
    LatencyQueryBenchmark,
    LatencyStageBreakdown,
    LatencyValidationResult,
)
from models.retrieval import RetrievalResult
from retrieval.latency_validator import (
    LatencyBenchmarkValidator,
    compute_standard_deviation,
    format_latency_markdown_report,
)
from retrieval.monitor import RetrievalMonitor


def _create_sample_eval_dataset() -> EvalDataset:
    """Create sample evaluation dataset with multiple domains."""
    items = [
        EvalDatasetItem(
            query_id=f"q_{idx}",
            query=f"Query number {idx} regarding enterprise policy and guidelines",
            ground_truth_answer="Answer reference text.",
            ground_truth_citations=[
                EvalGroundTruthCitation(
                    file_name="doc.pdf", page_number=1, chunk_id=f"chunk_{idx}"
                )
            ],
            is_out_of_corpus=False,
            category="sla" if idx % 2 == 0 else "security",
        )
        for idx in range(1, 11)
    ]
    items.append(
        EvalDatasetItem(
            query_id="q_out_1",
            query="Out of corpus recipe query",
            ground_truth_answer="I cannot answer this question based on the available documentation.",
            ground_truth_citations=[],
            is_out_of_corpus=True,
            category="out_of_corpus",
        )
    )
    return EvalDataset(items=items)


def test_validate_latency_sample_dataset() -> None:
    """Verify LatencyBenchmarkValidator passes and computes percentiles on sample dataset."""
    dataset = _create_sample_eval_dataset()
    validator = LatencyBenchmarkValidator(target_p95_latency_ms=3000.0)

    result = validator.validate(dataset=dataset, top_k=5)
    assert isinstance(result, LatencyValidationResult)
    assert result.passed is True
    assert result.measured_p95_latency_ms <= 3000.0
    assert result.target_threshold_ms == 3000.0
    assert result.total_queries == 11
    assert result.in_corpus_queries == 10
    assert result.out_of_corpus_queries == 1
    assert result.percentiles.p50_ms <= result.percentiles.p95_ms
    assert result.percentiles.p95_ms <= result.percentiles.p99_ms
    assert len(result.query_benchmarks) == 11
    assert "sla" in result.category_p95_latencies
    assert "security" in result.category_p95_latencies


def test_validate_latency_real_eval_dataset() -> None:
    """Verify p95_latency <= 3000ms on real 52-query eval_dataset.jsonl (Phase 10.6 SLA)."""
    dataset = load_eval_dataset_from_jsonl()
    validator = LatencyBenchmarkValidator(
        target_p95_latency_ms=3000.0,
        warmup_runs=1,
    )

    result = validator.validate(dataset=dataset, top_k=5)
    assert result.passed is True
    assert result.measured_p95_latency_ms <= 3000.0
    assert result.total_queries >= 50
    assert result.in_corpus_queries >= 40
    assert result.out_of_corpus_queries >= 10
    assert result.percentiles.mean_ms <= 1500.0


def test_latency_report_formatting_and_write(tmp_path: Path) -> None:
    """Verify latency markdown report rendering and filesystem persistence."""
    dataset = _create_sample_eval_dataset()
    report_file = tmp_path / "reports" / "latency_report.md"
    validator = LatencyBenchmarkValidator(target_p95_latency_ms=3000.0)

    result = validator.validate(dataset=dataset, output_report_path=report_file)
    assert result.passed is True
    assert report_file.is_file()

    content = report_file.read_text(encoding="utf-8")
    assert "# End-to-End Latency Benchmark Report (Phase 10.6)" in content
    assert "p_{95}" in content or "p_{95} Latency" in content
    assert "Domain Category P95 Breakdown" in content

    direct_report = format_latency_markdown_report(result)
    assert "Executive Summary" in direct_report


def test_validate_latency_threshold_violation_detection() -> None:
    """Verify validator flags failure when simulated latency exceeds SLA target."""
    dataset = _create_sample_eval_dataset()

    def slow_retriever(query: str, top_k: int) -> list[RetrievalResult]:
        time.sleep(0.01)  # small artificial delay
        return []

    monitor = RetrievalMonitor(retriever_fn=slow_retriever)
    # Set impossible tight SLA (0.001 ms)
    validator = LatencyBenchmarkValidator(
        monitor=monitor, target_p95_latency_ms=0.001, warmup_runs=0
    )

    result = validator.validate(dataset=dataset, top_k=5)
    assert result.passed is False
    assert result.measured_p95_latency_ms > 0.001


def test_validate_latency_empty_dataset_raises_error() -> None:
    """Verify validator raises EvaluationError when called with empty dataset."""
    validator = LatencyBenchmarkValidator()
    with pytest.raises(EvaluationError) as exc_info:
        validator.validate(dataset=EvalDataset(items=[]))
    assert exc_info.value.code == "EMPTY_EVAL_DATASET"


def test_compute_standard_deviation_utility() -> None:
    """Verify sample standard deviation calculation edge cases."""
    assert compute_standard_deviation([]) == 0.0
    assert compute_standard_deviation([42.0]) == 0.0
    val = compute_standard_deviation([10.0, 20.0, 30.0])
    assert val == 10.0


def test_latency_models_immutability() -> None:
    """Verify latency domain models enforce frozen immutability and forbid extra fields."""
    breakdown = LatencyStageBreakdown(
        retrieval_latency_ms=12.5,
        rerank_latency_ms=5.0,
        guard_latency_ms=0.5,
        generation_latency_ms=50.0,
        total_latency_ms=68.0,
    )
    with pytest.raises(ValueError):
        breakdown.total_latency_ms = 99.0  # type: ignore[misc]

    with pytest.raises(ValueError):
        LatencyQueryBenchmark(
            query_id="q1",
            query="test",
            latency_ms=10.0,
            unknown_arg="invalid",  # type: ignore[call-arg]
        )

    thresholds = LatencyMetricThresholds(max_p95_latency_ms=3000.0)
    assert thresholds.max_p95_latency_ms == 3000.0
