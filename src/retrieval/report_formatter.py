"""Markdown report generator and export utilities for RetrievalMonitor benchmarks."""

from collections import defaultdict
from pathlib import Path

from core.exceptions import EvaluationError
from models.evaluation import RetrievalBenchmarkReport, RetrievalQueryResult


def _format_status_badge(passed: bool) -> str:
    """Format pass/fail status badge with unicode indicator."""
    return "✅ PASS" if passed else "❌ FAIL"


def format_retrieval_markdown_report(report: RetrievalBenchmarkReport) -> str:
    """Format a comprehensive benchmark evaluation report in GitHub-flavored Markdown."""
    overall_status = _format_status_badge(report.all_passed)
    prec_status = _format_status_badge(report.precision_threshold_passed)
    hon_status = _format_status_badge(report.honesty_threshold_passed)
    lat_status = _format_status_badge(report.latency_threshold_passed)

    lines: list[str] = [
        "# Retrieval & Grounding Benchmark Report",
        "",
        f"> **Generated:** `{report.timestamp}` | **Overall Status:** {overall_status}",
        "",
        "## 1. Executive Summary & Quality Targets",
        "",
        "| Metric | Measured Value | Minimum Target | Evaluation Status |",
        "| :--- | :--- | :--- | :--- |",
        (
            f"| `retrieval_precision@5` | **{report.mean_precision_at_k:.4f}** | "
            f"$\\ge {report.thresholds.min_precision_at_5:.2f}$ | {prec_status} |"
        ),
        (
            f"| `honesty_filter_precision` | **{report.honesty_filter_precision:.4f}** | "
            f"$\\ge {report.thresholds.min_honesty_filter_precision:.2f}$ | {hon_status} |"
        ),
        (
            f"| `p95_latency_ms` | **{report.latency_p95_ms:.1f} ms** | "
            f"$\\le {report.thresholds.max_p95_latency_ms:.0f} \\text{{ ms}}$ | {lat_status} |"
        ),
        f"| `mean_recall@5` | **{report.mean_recall_at_k:.4f}** | — | INFO |",
        f"| `mrr` (Mean Reciprocal Rank) | **{report.mrr:.4f}** | — | INFO |",
        f"| `hit_rate@5` | **{report.hit_rate_at_k:.4f}** | — | INFO |",
        "",
        "## 2. Dataset & Cardinality Overview",
        "",
        f"- **Total Queries Evaluated:** {report.total_queries}",
        f"- **In-Corpus Factual Queries:** {report.in_corpus_queries}",
        f"- **Out-of-Corpus Refusal Queries:** {report.out_of_corpus_queries}",
        "",
        "## 3. Latency Distribution (Milliseconds)",
        "",
        "| Metric | Latency (ms) |",
        "| :--- | :--- |",
        f"| Median ($p_{{50}}$) | {report.latency_p50_ms:.2f} ms |",
        f"| 90th Percentile ($p_{{90}}$) | {report.latency_p90_ms:.2f} ms |",
        f"| 95th Percentile ($p_{{95}}$) | {report.latency_p95_ms:.2f} ms |",
        f"| 99th Percentile ($p_{{99}}$) | {report.latency_p99_ms:.2f} ms |",
        f"| Mean Latency | {report.latency_mean_ms:.2f} ms |",
        f"| Maximum Latency | {report.latency_max_ms:.2f} ms |",
        "",
        "## 4. Category Breakdown",
        "",
        "| Category | Count | Precision@5 | Recall@5 | MRR | Hit Rate | Guard Pass Rate |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    cat_map: dict[str, list[RetrievalQueryResult]] = defaultdict(list)
    for q in report.query_results:
        cat_map[q.category].append(q)

    for cat_name in sorted(cat_map.keys()):
        items = cat_map[cat_name]
        c_total = len(items)
        c_prec = sum(q.precision_at_k for q in items) / c_total
        c_rec = sum(q.recall_at_k for q in items) / c_total
        c_mrr = sum(q.reciprocal_rank for q in items) / c_total
        c_hit = sum(1 for q in items if q.hit_at_k) / c_total
        c_pass = sum(1 for q in items if q.passed_confidence_guard) / c_total

        lines.append(
            f"| `{cat_name}` | {c_total} | {c_prec:.3f} | {c_rec:.3f} | {c_mrr:.3f} | {c_hit:.3f} | {c_pass:.3f} |"
        )

    # Failed queries section
    failed_in_corpus = [
        q
        for q in report.query_results
        if not q.is_out_of_corpus and q.precision_at_k < 0.2
    ]
    failed_refusal = [
        q
        for q in report.query_results
        if q.is_out_of_corpus and not q.is_correctly_refused
    ]

    if failed_in_corpus or failed_refusal:
        lines.extend(
            [
                "",
                "## 5. Failure & Outlier Inspection",
                "",
                "| Query ID | Category | Type | Query Text | Issue |",
                "| :--- | :--- | :--- | :--- | :--- |",
            ]
        )
        for q in failed_in_corpus[:10]:
            lines.append(
                f"| `{q.query_id}` | `{q.category}` | In-Corpus | {q.query[:50]}... | Low Precision ({q.precision_at_k:.2f}) |"
            )
        for q in failed_refusal[:10]:
            lines.append(
                f"| `{q.query_id}` | `{q.category}` | Out-of-Corpus | {q.query[:50]}... | Failed Refusal (Guard Passed) |"
            )

    lines.append("")
    return "\n".join(lines)


def write_retrieval_markdown_report(
    report: RetrievalBenchmarkReport,
    output_path: Path | str,
) -> Path:
    """Write rendered markdown benchmark report to target filesystem path."""
    target = Path(output_path)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        rendered_md = format_retrieval_markdown_report(report)
        with open(target, "w", encoding="utf-8") as f:
            f.write(rendered_md)
        return target
    except OSError as exc:
        raise EvaluationError(
            message=f"Failed to write benchmark report to {target}: {exc}",
            code="REPORT_WRITE_ERROR",
            details={"path": str(target), "error": str(exc)},
        ) from exc
