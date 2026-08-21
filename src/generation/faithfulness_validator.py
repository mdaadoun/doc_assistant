"""RAGAS Faithfulness validator verifying faithfulness_score >= 0.85."""

from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import structlog

from core.eval_dataset import load_eval_dataset_from_jsonl
from core.exceptions import EvaluationError
from generation.faithfulness import RAGASFaithfulnessEvaluator
from models.evaluation import EvalDataset
from models.faithfulness import (
    FaithfulnessQueryResult,
    FaithfulnessValidationResult,
)

logger = structlog.get_logger(__name__)


def format_faithfulness_markdown_report(
    result: FaithfulnessValidationResult,
) -> str:
    """Format a comprehensive RAGAS faithfulness benchmark evaluation report in Markdown."""
    status_badge = "✅ PASS" if result.passed else "❌ FAIL"

    lines: list[str] = [
        "# RAGAS Faithfulness Benchmark Report",
        "",
        f"> **Generated:** `{result.timestamp}` | **Overall Status:** {status_badge}",
        "",
        "## 1. Executive Summary & Quality Targets",
        "",
        "| Metric | Measured Value | Target Threshold | Status |",
        "| :--- | :--- | :--- | :--- |",
        (
            f"| `faithfulness_score` | **{result.mean_faithfulness_score:.4f}** | "
            f"$\\ge {result.target_threshold:.2f}$ | {status_badge} |"
        ),
        "",
        "## 2. Dataset Overview",
        "",
        f"- **Total Queries Evaluated:** {result.total_queries}",
        f"- **In-Corpus Factual Queries:** {result.in_corpus_queries}",
        f"- **Out-of-Corpus Refusal Queries:** {result.out_of_corpus_queries}",
        "",
        "## 3. Category Breakdown",
        "",
        "| Category | Mean Faithfulness Score | Status |",
        "| :--- | :--- | :--- |",
    ]

    for cat_name in sorted(result.category_scores.keys()):
        score = result.category_scores[cat_name]
        cat_badge = "✅ PASS" if score >= result.target_threshold else "❌ FAIL"
        lines.append(f"| `{cat_name}` | {score:.4f} | {cat_badge} |")

    # Unfaithful queries section if any
    unfaithful = [q for q in result.query_results if not q.is_faithful]
    if unfaithful:
        lines.extend(
            [
                "",
                "## 4. Unfaithful or Hallucinated Queries",
                "",
                "| Query ID | Category | Query Text | Score | Reason |",
                "| :--- | :--- | :--- | :--- | :--- |",
            ]
        )
        for q in unfaithful[:10]:
            stmt_reasons = "; ".join(
                v.reason for v in q.verifications if not v.is_faithful
            )
            lines.append(
                f"| `{q.query_id}` | `{q.category}` | {q.query[:45]}... | {q.faithfulness_score:.2f} | {stmt_reasons[:60]} |"
            )

    lines.append("")
    return "\n".join(lines)


def write_faithfulness_markdown_report(
    result: FaithfulnessValidationResult,
    output_path: Path | str,
) -> Path:
    """Write rendered markdown faithfulness benchmark report to target filesystem path."""
    target = Path(output_path)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        rendered_md = format_faithfulness_markdown_report(result)
        with open(target, "w", encoding="utf-8") as f:
            f.write(rendered_md)
        return target
    except OSError as exc:
        raise EvaluationError(
            message=f"Failed to write faithfulness report to {target}: {exc}",
            code="REPORT_WRITE_ERROR",
            details={"path": str(target), "error": str(exc)},
        ) from exc


class FaithfulnessValidator:
    """Validates faithfulness_score meets or exceeds target threshold (>= 0.85)."""

    def __init__(
        self,
        min_faithfulness_threshold: float = 0.85,
        evaluator: type[RAGASFaithfulnessEvaluator] | None = None,
    ) -> None:
        """Initialize validator with target threshold and evaluator class."""
        self.min_faithfulness_threshold = min_faithfulness_threshold
        self.evaluator = evaluator or RAGASFaithfulnessEvaluator

    def validate(
        self,
        dataset: EvalDataset | None = None,
        dataset_path: Path | str | None = None,
        output_report_path: Path | str | None = None,
    ) -> FaithfulnessValidationResult:
        """Run RAGAS faithfulness validation against dataset and return structured report."""
        target_dataset = (
            dataset
            if dataset is not None
            else load_eval_dataset_from_jsonl(dataset_path)
        )
        if not target_dataset.items:
            raise EvaluationError(
                message="Cannot validate faithfulness on empty evaluation dataset.",
                code="EMPTY_EVAL_DATASET",
            )

        query_results: list[FaithfulnessQueryResult] = []

        for item in target_dataset.items:
            # Build context list from ground-truth citations or text
            if item.is_out_of_corpus:
                contexts: Sequence[str | dict[str, Any]] = []
            else:
                contexts = [
                    {
                        "chunk_id": gt.chunk_id,
                        "file_name": gt.file_name,
                        "page_number": gt.page_number,
                        "text": (
                            f"{gt.excerpt} {item.ground_truth_answer}"
                            if gt.excerpt
                            else item.ground_truth_answer
                        ),
                    }
                    for gt in item.ground_truth_citations
                ]


            result = self.evaluator.evaluate_answer(
                query=item.query,
                answer=item.ground_truth_answer,
                contexts=contexts,
                is_out_of_corpus=item.is_out_of_corpus,
                query_id=item.query_id,
                category=item.category,
                min_threshold=self.min_faithfulness_threshold,
            )
            query_results.append(result)

        # Aggregate category scores
        cat_map = defaultdict(list)
        for q in query_results:
            cat_map[q.category].append(q.faithfulness_score)

        category_scores: dict[str, float] = {
            cat_name: round(sum(scores) / len(scores), 4)
            for cat_name, scores in cat_map.items()
        }

        total_queries = len(query_results)
        in_corpus_count = sum(1 for q in query_results if not q.is_out_of_corpus)
        out_of_corpus_count = sum(1 for q in query_results if q.is_out_of_corpus)

        mean_faithfulness = (
            sum(q.faithfulness_score for q in query_results) / total_queries
            if total_queries > 0
            else 0.0
        )
        passed = mean_faithfulness >= self.min_faithfulness_threshold

        validation_result = FaithfulnessValidationResult(
            passed=passed,
            mean_faithfulness_score=round(mean_faithfulness, 4),
            target_threshold=self.min_faithfulness_threshold,
            total_queries=total_queries,
            in_corpus_queries=in_corpus_count,
            out_of_corpus_queries=out_of_corpus_count,
            category_scores=category_scores,
            query_results=query_results,
        )

        if output_report_path is not None:
            write_faithfulness_markdown_report(validation_result, output_report_path)

        logger.info(
            "faithfulness_validated",
            mean_faithfulness=validation_result.mean_faithfulness_score,
            target_threshold=self.min_faithfulness_threshold,
            passed=passed,
            total_queries=total_queries,
        )

        return validation_result
