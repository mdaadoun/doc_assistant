"""Unit tests for HonestyFilterValidator verifying honesty_filter_precision >= 0.90."""

from pathlib import Path

import pytest

from core.eval_dataset import load_eval_dataset_from_jsonl
from core.exceptions import EvaluationError
from models.evaluation import (
    EvalDataset,
    EvalDatasetItem,
    EvalGroundTruthCitation,
)
from models.honesty import (
    HonestyConfusionMatrix,
    HonestyMetricThresholds,
    HonestyQueryClassification,
    HonestyValidationResult,
)
from models.retrieval import RetrievalResult
from retrieval.honesty_validator import (
    HonestyFilterValidator,
    format_honesty_markdown_report,
)
from retrieval.monitor import RetrievalMonitor


def _create_sample_eval_dataset() -> EvalDataset:
    """Create a sample dataset with balanced in-corpus and out-of-corpus queries."""
    sample_in_corpus = [
        (
            "q_sla_1",
            "What is the notice period for contract termination under standard SLAs?",
            "Notice period is 30 calendar days.",
            "sla.pdf",
            1,
            "chunk_sla_1",
            "sla",
        ),
        (
            "q_sec_1",
            "How often must employee passwords be rotated according to security policy?",
            "Passwords must be changed every 90 days.",
            "security.pdf",
            1,
            "chunk_sec_1",
            "security",
        ),
        (
            "q_hr_1",
            "How many days of paid time off do employees receive annually?",
            "Employees receive 25 days of paid leave.",
            "hr.docx",
            1,
            "chunk_hr_1",
            "hr_policy",
        ),
    ]

    items = [
        EvalDatasetItem(
            query_id=qid,
            query=q,
            ground_truth_answer=ans,
            ground_truth_citations=[
                EvalGroundTruthCitation(
                    file_name=fn, page_number=pn, chunk_id=cid, excerpt=ans
                )
            ],
            is_out_of_corpus=False,
            category=cat,
        )
        for qid, q, ans, fn, pn, cid, cat in sample_in_corpus
    ]

    sample_out_of_corpus = [
        ("q_out_1", "What is the recipe for authentic Neapolitan pizza dough?"),
        ("q_out_2", "Who won the FIFA World Cup football tournament in 1998?"),
        ("q_out_3", "How do you calculate the Schwarzschild radius of a black hole?"),
    ]

    for qid, q in sample_out_of_corpus:
        items.append(
            EvalDatasetItem(
                query_id=qid,
                query=q,
                ground_truth_answer="I cannot answer this question based on the available documentation.",
                ground_truth_citations=[],
                is_out_of_corpus=True,
                category="out_of_corpus",
            )
        )

    return EvalDataset(items=items)


def test_validate_honesty_on_sample_dataset() -> None:
    """Verify HonestyFilterValidator achieves 100% precision on sample dataset."""
    dataset = _create_sample_eval_dataset()
    validator = HonestyFilterValidator(min_honesty_threshold=0.90)

    result = validator.validate(dataset=dataset, top_k=5)
    assert isinstance(result, HonestyValidationResult)
    assert result.passed is True
    assert result.measured_honesty_precision >= 0.90
    assert result.target_threshold == 0.90
    assert result.total_queries == 6
    assert result.in_corpus_queries == 3
    assert result.out_of_corpus_queries == 3
    assert result.true_refusals == 3
    assert result.false_acceptances == 0
    assert result.true_acceptances == 3
    assert result.false_refusals == 0
    assert result.out_of_corpus_refusal_rate == 1.0
    assert result.in_corpus_pass_rate == 1.0
    assert result.false_refusal_rate == 0.0
    assert result.confusion_matrix.true_refusals == 3
    assert len(result.query_classifications) == 6


def test_validate_honesty_on_real_eval_dataset() -> None:
    """Verify honesty_filter_precision >= 0.90 on real 52-query eval_dataset.jsonl."""
    dataset = load_eval_dataset_from_jsonl()
    validator = HonestyFilterValidator(min_honesty_threshold=0.90)

    result = validator.validate(dataset=dataset, top_k=5)
    assert result.passed is True
    assert result.measured_honesty_precision >= 0.90
    assert result.total_queries >= 50
    assert result.in_corpus_queries >= 40
    assert result.out_of_corpus_queries >= 10
    assert result.true_refusals >= 9
    assert result.false_acceptances <= 1
    assert result.out_of_corpus_refusal_rate >= 0.90


def test_write_and_format_honesty_report(tmp_path: Path) -> None:
    """Verify markdown report rendering and filesystem persistence."""
    dataset = _create_sample_eval_dataset()
    report_file = tmp_path / "reports" / "honesty_report.md"
    validator = HonestyFilterValidator(min_honesty_threshold=0.90)

    result = validator.validate(dataset=dataset, output_report_path=report_file)
    assert result.passed is True
    assert report_file.is_file()

    content = report_file.read_text(encoding="utf-8")
    assert "# Honesty Filter Precision Benchmark Report (Phase 10.5)" in content
    assert "honesty_filter_precision" in content
    assert "Confusion Matrix" in content
    assert "Out-of-Corpus Query Refusal Audit" in content

    rendered_direct = format_honesty_markdown_report(result)
    assert "Executive Summary" in rendered_direct


def test_validate_honesty_failure_on_false_acceptances() -> None:
    """Verify validator fails when out-of-corpus queries bypass confidence filter."""
    dataset = _create_sample_eval_dataset()

    def always_confident_retriever(query: str, top_k: int) -> list[RetrievalResult]:
        return [
            RetrievalResult(
                chunk_id="hallucinated_chunk",
                text="fake content",
                file_name="fake.pdf",
                page_number=1,
                relevance_score=0.99,
                retrieval_method="hybrid",
            )
        ]

    monitor = RetrievalMonitor(retriever_fn=always_confident_retriever)
    validator = HonestyFilterValidator(monitor=monitor, min_honesty_threshold=0.90)

    result = validator.validate(dataset=dataset, top_k=5)
    assert result.passed is False
    assert result.measured_honesty_precision == 0.0
    assert result.false_acceptances == 3
    assert result.true_refusals == 0


def test_validate_honesty_empty_dataset_raises_error() -> None:
    """Verify validator raises EvaluationError on empty dataset."""
    validator = HonestyFilterValidator()
    with pytest.raises(EvaluationError) as exc_info:
        validator.validate(dataset=EvalDataset(items=[]))
    assert exc_info.value.code == "EMPTY_EVAL_DATASET"


def test_honesty_models_immutability() -> None:
    """Verify honesty domain models enforce frozen immutability and forbid extra fields."""
    item = HonestyQueryClassification(
        query_id="q1",
        query="Test query",
        category="general",
        is_out_of_corpus=True,
        expected_refusal=True,
        system_refused=True,
        is_correctly_classified=True,
    )
    with pytest.raises(ValueError):
        item.is_correctly_classified = False

    with pytest.raises(ValueError):
        HonestyConfusionMatrix(true_refusals=1, unknown_field=123)  # type: ignore[call-arg]

    thresholds = HonestyMetricThresholds(min_honesty_filter_precision=0.90)
    assert thresholds.min_honesty_filter_precision == 0.90
