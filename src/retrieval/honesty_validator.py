"""Honesty filter precision validator verifying honesty_filter_precision >= 0.90."""

from collections import defaultdict
from pathlib import Path

import structlog

from core.eval_dataset import load_eval_dataset_from_jsonl
from core.exceptions import EvaluationError
from models.evaluation import EvalDataset
from models.honesty import (
    HonestyConfusionMatrix,
    HonestyQueryClassification,
    HonestyValidationResult,
)
from retrieval.confidence_guard import ConfidenceGuard
from retrieval.monitor import RetrievalMonitor
from retrieval.precision_validator import (
    build_corpus_chunks_from_dataset,
    create_calibrated_retrieval_monitor,
)

logger = structlog.get_logger(__name__)


def format_honesty_markdown_report(result: HonestyValidationResult) -> str:
    """Render structured Markdown benchmark report for honesty filter evaluation."""
    lines: list[str] = [
        "# Honesty Filter Precision Benchmark Report (Phase 10.5)",
        "",
        f"**Timestamp:** {result.timestamp} | **Status:** {'PASSED' if result.passed else 'FAILED'}",
        "",
        "## Executive Summary",
        "",
        "| Metric | Measured | Target Threshold | Status |",
        "| :--- | :--- | :--- | :--- |",
        f"| `honesty_filter_precision` | {result.measured_honesty_precision:.2%} | >= {result.target_threshold:.2%} | {'PASS' if result.passed else 'FAIL'} |",
        f"| `out_of_corpus_refusal_rate` | {result.out_of_corpus_refusal_rate:.2%} | >= {result.target_threshold:.2%} | {'PASS' if result.out_of_corpus_refusal_rate >= result.target_threshold else 'FAIL'} |",
        f"| `in_corpus_pass_rate` | {result.in_corpus_pass_rate:.2%} | >= 90.00% | {'PASS' if result.in_corpus_pass_rate >= 0.90 else 'FAIL'} |",
        f"| `false_refusal_rate` | {result.false_refusal_rate:.2%} | <= 10.00% | {'PASS' if result.false_refusal_rate <= 0.10 else 'FAIL'} |",
        "",
        "## Confusion Matrix",
        "",
        "| Ground Truth Scope | System Refused (Low Confidence) | System Accepted (Grounded) | Total |",
        "| :--- | :--- | :--- | :--- |",
        f"| **Out-of-Corpus** | {result.confusion_matrix.true_refusals} (True Refusal) | {result.confusion_matrix.false_acceptances} (False Acceptance) | {result.out_of_corpus_queries} |",
        f"| **In-Corpus** | {result.confusion_matrix.false_refusals} (False Refusal) | {result.confusion_matrix.true_acceptances} (True Acceptance) | {result.in_corpus_queries} |",
        f"| **Total** | {result.confusion_matrix.true_refusals + result.confusion_matrix.false_refusals} | {result.confusion_matrix.false_acceptances + result.confusion_matrix.true_acceptances} | {result.total_queries} |",
        "",
        "## Domain Category Breakdown",
        "",
        "| Domain Category | Evaluated Queries | Accuracy / Precision |",
        "| :--- | :--- | :--- |",
    ]

    for cat_name, score in sorted(result.category_metrics.items()):
        lines.append(f"| `{cat_name}` | - | {score:.2%} |")

    lines.extend(
        [
            "",
            "## Out-of-Corpus Query Refusal Audit",
            "",
            "| Query ID | Query | Top Score | Refused? | Status |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
    )

    for q in result.query_classifications:
        if q.is_out_of_corpus:
            status = "CORRECT" if q.is_correctly_classified else "HALLUCINATION_RISK"
            refused_str = "YES" if q.system_refused else "NO"
            trunc_query = q.query[:60] + "..." if len(q.query) > 60 else q.query
            lines.append(
                f"| `{q.query_id}` | {trunc_query} | {q.confidence_score:.3f} | {refused_str} | {status} |"
            )

    lines.append("")
    return "\n".join(lines)


def write_honesty_markdown_report(
    result: HonestyValidationResult,
    output_path: Path | str,
) -> Path:
    """Format and write honesty filter benchmark report to filesystem path."""
    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    report_text = format_honesty_markdown_report(result)
    dest.write_text(report_text, encoding="utf-8")
    return dest


class HonestyFilterValidator:
    """Validates that honesty_filter_precision meets or exceeds required target (>= 0.90)."""

    def __init__(
        self,
        monitor: RetrievalMonitor | None = None,
        confidence_guard: ConfidenceGuard | None = None,
        min_honesty_threshold: float = 0.90,
        max_false_refusal_rate: float = 0.10,
    ) -> None:
        """Initialize validator with optional custom monitor, guard, and target threshold."""
        self.monitor = monitor
        self.confidence_guard = confidence_guard or ConfidenceGuard(threshold=0.35)
        self.min_honesty_threshold = min_honesty_threshold
        self.max_false_refusal_rate = max_false_refusal_rate

    def validate(
        self,
        dataset: EvalDataset | None = None,
        dataset_path: Path | str | None = None,
        top_k: int = 5,
        output_report_path: Path | str | None = None,
    ) -> HonestyValidationResult:
        """Run honesty filter validation against evaluation dataset and return structured metrics."""
        target_dataset = (
            dataset
            if dataset is not None
            else load_eval_dataset_from_jsonl(dataset_path)
        )
        if not target_dataset.items:
            raise EvaluationError(
                message="Cannot validate honesty filter precision on empty evaluation dataset.",
                code="EMPTY_EVAL_DATASET",
            )

        active_monitor = self.monitor
        if active_monitor is None:
            corpus_chunks = build_corpus_chunks_from_dataset(target_dataset)
            active_monitor = create_calibrated_retrieval_monitor(
                corpus_chunks, threshold=0.75
            )

        classifications: list[HonestyQueryClassification] = []
        tr, fa, ta, fr = 0, 0, 0, 0
        cat_correct: dict[str, int] = defaultdict(int)
        cat_total: dict[str, int] = defaultdict(int)

        for item in target_dataset.items:
            query_res = active_monitor.evaluate_item(item, top_k=top_k)
            system_refused = not query_res.passed_confidence_guard
            expected_refusal = item.is_out_of_corpus
            is_correct = expected_refusal == system_refused

            cat_total[item.category] += 1
            if is_correct:
                cat_correct[item.category] += 1

            if item.is_out_of_corpus:
                if system_refused:
                    tr += 1
                    reason = (
                        "Correctly refused out-of-corpus query below confidence cutoff."
                    )
                else:
                    fa += 1
                    reason = "False acceptance: out-of-corpus query exceeded confidence cutoff."
            else:
                if not system_refused:
                    ta += 1
                    reason = (
                        "Correctly accepted in-corpus query meeting confidence cutoff."
                    )
                else:
                    fr += 1
                    reason = (
                        "False refusal: in-corpus query fell below confidence cutoff."
                    )

            classifications.append(
                HonestyQueryClassification(
                    query_id=item.query_id,
                    query=item.query,
                    category=item.category,
                    is_out_of_corpus=item.is_out_of_corpus,
                    expected_refusal=expected_refusal,
                    system_refused=system_refused,
                    is_correctly_classified=is_correct,
                    confidence_score=query_res.top_score,
                    relevance_threshold=self.confidence_guard.threshold,
                    refusal_reason=reason,
                )
            )

        out_count = target_dataset.out_of_corpus_count
        in_count = target_dataset.in_corpus_count
        measured_honesty = float(tr) / float(out_count) if out_count > 0 else 1.0
        in_pass_rate = float(ta) / float(in_count) if in_count > 0 else 1.0
        false_refusal_rate = float(fr) / float(in_count) if in_count > 0 else 0.0

        passed = (
            measured_honesty >= self.min_honesty_threshold
            and false_refusal_rate <= self.max_false_refusal_rate
        )

        category_metrics = {
            cat: round(float(cat_correct[cat]) / float(cat_total[cat]), 4)
            for cat in cat_total
        }

        matrix = HonestyConfusionMatrix(
            true_refusals=tr,
            false_acceptances=fa,
            true_acceptances=ta,
            false_refusals=fr,
        )

        result = HonestyValidationResult(
            passed=passed,
            measured_honesty_precision=round(measured_honesty, 4),
            target_threshold=self.min_honesty_threshold,
            total_queries=target_dataset.total_queries,
            in_corpus_queries=in_count,
            out_of_corpus_queries=out_count,
            true_refusals=tr,
            false_acceptances=fa,
            true_acceptances=ta,
            false_refusals=fr,
            out_of_corpus_refusal_rate=round(measured_honesty, 4),
            in_corpus_pass_rate=round(in_pass_rate, 4),
            false_refusal_rate=round(false_refusal_rate, 4),
            confusion_matrix=matrix,
            category_metrics=category_metrics,
            query_classifications=classifications,
        )

        if output_report_path is not None:
            write_honesty_markdown_report(result, output_report_path)

        logger.info(
            "honesty_filter_validated",
            honesty_precision=measured_honesty,
            target_threshold=self.min_honesty_threshold,
            passed=passed,
            true_refusals=tr,
            false_acceptances=fa,
            true_acceptances=ta,
            false_refusals=fr,
        )

        return result
