"""Latency benchmark validator verifying p95_latency <= 3000ms SLA threshold."""

import math
import time
from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path

import structlog

from core.eval_dataset import load_eval_dataset_from_jsonl
from core.exceptions import EvaluationError
from models.evaluation import EvalDataset
from models.latency import (
    LatencyMetricThresholds,
    LatencyPercentileMetrics,
    LatencyQueryBenchmark,
    LatencyValidationResult,
)
from retrieval.metrics import compute_latency_statistics, compute_percentile
from retrieval.monitor import RetrievalMonitor
from retrieval.precision_validator import (
    build_corpus_chunks_from_dataset,
    create_calibrated_retrieval_monitor,
)

logger = structlog.get_logger(__name__)


def compute_standard_deviation(values: Sequence[float]) -> float:
    """Compute sample standard deviation of numerical series in ms."""
    if len(values) <= 1:
        return 0.0
    mean_val = sum(values) / len(values)
    variance = sum((x - mean_val) ** 2 for x in values) / (len(values) - 1)
    return round(math.sqrt(variance), 3)


def format_latency_markdown_report(result: LatencyValidationResult) -> str:
    """Render structured Markdown benchmark report for latency SLA verification."""
    p = result.percentiles
    lines: list[str] = [
        "# End-to-End Latency Benchmark Report (Phase 10.6)",
        "",
        f"**Timestamp:** {result.timestamp} | **Status:** {'PASSED' if result.passed else 'FAILED'}",
        "",
        "## Executive Summary",
        "",
        "| Latency Metric | Measured (ms) | SLA Threshold (ms) | Status |",
        "| :--- | :--- | :--- | :--- |",
        f"| **$p_{{95}}$ Latency** | {p.p95_ms:.2f} ms | <= {result.target_threshold_ms:.2f} ms | {'PASS' if result.passed else 'FAIL'} |",
        f"| **$p_{{50}}$ (Median)** | {p.p50_ms:.2f} ms | <= 1000.00 ms | {'PASS' if p.p50_ms <= 1000.0 else 'WARN'} |",
        f"| **$p_{{90}}$ Latency** | {p.p90_ms:.2f} ms | <= 2500.00 ms | {'PASS' if p.p90_ms <= 2500.0 else 'WARN'} |",
        f"| **$p_{{99}}$ Latency** | {p.p99_ms:.2f} ms | <= {result.thresholds.max_p99_latency_ms:.2f} ms | {'PASS' if p.p99_ms <= result.thresholds.max_p99_latency_ms else 'FAIL'} |",
        f"| **Mean Latency** | {p.mean_ms:.2f} ms | <= {result.thresholds.max_mean_latency_ms:.2f} ms | {'PASS' if p.mean_ms <= result.thresholds.max_mean_latency_ms else 'FAIL'} |",
        f"| **Min / Max** | {p.min_ms:.2f} / {p.max_ms:.2f} ms | - | INFO |",
        f"| **Std Deviation** | {p.std_dev_ms:.2f} ms | - | INFO |",
        "",
        "## Domain Category P95 Breakdown",
        "",
        "| Category | Evaluated Queries | Measured $p_{95}$ (ms) | SLA Compliance |",
        "| :--- | :--- | :--- | :--- |",
    ]

    for cat_name, p95_val in sorted(result.category_p95_latencies.items()):
        status_str = "PASS" if p95_val <= result.target_threshold_ms else "FAIL"
        lines.append(f"| `{cat_name}` | - | {p95_val:.2f} ms | {status_str} |")

    lines.extend(
        [
            "",
            "## Query Latency Sample Audit",
            "",
            "| Query ID | Category | Latency (ms) | Status |",
            "| :--- | :--- | :--- | :--- |",
        ]
    )

    for q in result.query_benchmarks[:10]:
        lines.append(
            f"| `{q.query_id}` | `{q.category}` | {q.latency_ms:.2f} ms | {q.status} |"
        )

    if len(result.query_benchmarks) > 10:
        lines.append(
            f"| *... and {len(result.query_benchmarks) - 10} more queries* | | | |"
        )

    lines.append("")
    return "\n".join(lines)


def write_latency_markdown_report(
    result: LatencyValidationResult,
    output_path: Path | str,
) -> Path:
    """Format and write latency benchmark report to filesystem path."""
    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    report_text = format_latency_markdown_report(result)
    dest.write_text(report_text, encoding="utf-8")
    return dest


class LatencyBenchmarkValidator:
    """Validates that end-to-end pipeline latency satisfies p95_latency <= 3000ms."""

    def __init__(
        self,
        monitor: RetrievalMonitor | None = None,
        target_p95_latency_ms: float = 3000.0,
        max_mean_latency_ms: float = 1500.0,
        max_p99_latency_ms: float = 5000.0,
        warmup_runs: int = 1,
    ) -> None:
        """Initialize validator with optional custom monitor and SLA thresholds."""
        self.monitor = monitor
        self.target_p95_latency_ms = target_p95_latency_ms
        self.max_mean_latency_ms = max_mean_latency_ms
        self.max_p99_latency_ms = max_p99_latency_ms
        self.warmup_runs = max(0, warmup_runs)

    def validate(
        self,
        dataset: EvalDataset | None = None,
        dataset_path: Path | str | None = None,
        top_k: int = 5,
        output_report_path: Path | str | None = None,
    ) -> LatencyValidationResult:
        """Run latency benchmarking over evaluation dataset and verify SLA thresholds."""
        target_dataset = (
            dataset
            if dataset is not None
            else load_eval_dataset_from_jsonl(dataset_path)
        )
        if not target_dataset.items:
            raise EvaluationError(
                message="Cannot validate latency on empty evaluation dataset.",
                code="EMPTY_EVAL_DATASET",
            )

        active_monitor = self.monitor
        if active_monitor is None:
            corpus_chunks = build_corpus_chunks_from_dataset(target_dataset)
            active_monitor = create_calibrated_retrieval_monitor(
                corpus_chunks, threshold=0.75
            )

        for _ in range(self.warmup_runs):
            for item in target_dataset.items[:3]:
                active_monitor.evaluate_item(item, top_k=top_k)

        query_benchmarks: list[LatencyQueryBenchmark] = []
        latencies: list[float] = []
        cat_latencies: dict[str, list[float]] = defaultdict(list)

        for item in target_dataset.items:
            start_t = time.perf_counter()
            query_res = active_monitor.evaluate_item(item, top_k=top_k)
            duration_ms = (time.perf_counter() - start_t) * 1000.0

            measured_duration = max(0.001, round(duration_ms, 3))
            latencies.append(measured_duration)
            cat_latencies[item.category].append(measured_duration)

            status_str = "ERROR" if query_res.error else "OK"
            query_benchmarks.append(
                LatencyQueryBenchmark(
                    query_id=item.query_id,
                    query=item.query,
                    category=item.category,
                    is_out_of_corpus=item.is_out_of_corpus,
                    latency_ms=measured_duration,
                    status=status_str,
                    error_message=query_res.error,
                )
            )

        stats = compute_latency_statistics(latencies)
        min_v = min(latencies) if latencies else 0.0
        max_v = max(latencies) if latencies else 0.0
        std_dev = compute_standard_deviation(latencies)

        percentiles = LatencyPercentileMetrics(
            p50_ms=stats["p50_ms"],
            p90_ms=stats["p90_ms"],
            p95_ms=stats["p95_ms"],
            p99_ms=stats["p99_ms"],
            mean_ms=stats["mean_ms"],
            min_ms=round(min_v, 3),
            max_ms=round(max_v, 3),
            std_dev_ms=std_dev,
        )

        category_p95: dict[str, float] = {
            cat: round(compute_percentile(vals, 95.0), 3)
            for cat, vals in cat_latencies.items()
        }

        measured_p95 = percentiles.p95_ms
        passed = (
            measured_p95 <= self.target_p95_latency_ms
            and percentiles.mean_ms <= self.max_mean_latency_ms
            and percentiles.p99_ms <= self.max_p99_latency_ms
        )

        thresholds = LatencyMetricThresholds(
            max_p95_latency_ms=self.target_p95_latency_ms,
            max_mean_latency_ms=self.max_mean_latency_ms,
            max_p99_latency_ms=self.max_p99_latency_ms,
        )

        result = LatencyValidationResult(
            passed=passed,
            measured_p95_latency_ms=measured_p95,
            target_threshold_ms=self.target_p95_latency_ms,
            total_queries=target_dataset.total_queries,
            in_corpus_queries=target_dataset.in_corpus_count,
            out_of_corpus_queries=target_dataset.out_of_corpus_count,
            percentiles=percentiles,
            thresholds=thresholds,
            category_p95_latencies=category_p95,
            query_benchmarks=query_benchmarks,
        )

        if output_report_path is not None:
            write_latency_markdown_report(result, output_report_path)

        logger.info(
            "latency_benchmark_validated",
            p95_ms=measured_p95,
            target_p95_ms=self.target_p95_latency_ms,
            mean_ms=percentiles.mean_ms,
            passed=passed,
            total_queries=len(query_benchmarks),
        )

        return result
