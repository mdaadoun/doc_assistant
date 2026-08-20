"""Unit tests for RetrievalPrecisionValidator verifying retrieval_precision@5 >= 0.75."""

from pathlib import Path

import pytest

from core.eval_dataset import load_eval_dataset_from_jsonl
from core.exceptions import EvaluationError
from models.evaluation import (
    EvalDataset,
    EvalDatasetItem,
    EvalGroundTruthCitation,
    RetrievalPrecisionValidationResult,
)
from models.retrieval import RetrievalResult
from retrieval.monitor import RetrievalMonitor
from retrieval.precision_validator import (
    RetrievalPrecisionValidator,
    build_corpus_chunks_from_dataset,
    create_calibrated_retrieval_monitor,
)


def _create_sample_eval_dataset() -> EvalDataset:
    """Create a multi-category sample evaluation dataset."""
    sample_records = [
        (
            "q_sla_1",
            "What is the mandatory notice period for contract termination under standard SLAs?",
            "Written notice period of 30 calendar days for termination.",
            "sla.pdf",
            1,
            "chunk_sla_1",
            "sla",
        ),
        (
            "q_sla_2",
            "What is the guaranteed monthly system uptime availability percentage?",
            "Monthly availability level guarantee of 99.9% uptime.",
            "sla.pdf",
            2,
            "chunk_sla_2",
            "sla",
        ),
        (
            "q_sla_3",
            "What is the target response time for Priority 1 critical service outages?",
            "Initial response time within 15 minutes for critical outages.",
            "sla.pdf",
            3,
            "chunk_sla_3",
            "sla",
        ),
        (
            "q_sla_4",
            "What penalty service credit percentage is issued when uptime drops?",
            "A service credit equal to 25% of billing fee is credited.",
            "sla.pdf",
            4,
            "chunk_sla_4",
            "sla",
        ),
        (
            "q_sla_5",
            "When are scheduled maintenance windows permitted to take place on Sundays?",
            "Scheduled maintenance on Sundays between 02:00 and 06:00 UTC.",
            "sla.pdf",
            5,
            "chunk_sla_5",
            "sla",
        ),
        (
            "q_sec_1",
            "How often must corporate employee passwords be rotated?",
            "User passwords must be changed every 90 days with history check.",
            "security.pdf",
            1,
            "chunk_sec_1",
            "security",
        ),
        (
            "q_sec_2",
            "Which systems mandate multi-factor authentication MFA enforcement?",
            "MFA is mandatory for VPN, email, and cloud management consoles.",
            "security.pdf",
            2,
            "chunk_sec_2",
            "security",
        ),
        (
            "q_sec_3",
            "What encryption algorithms are required for data at rest and in transit?",
            "Data at rest requires AES-256 encryption and TLS 1.3 in transit.",
            "security.pdf",
            3,
            "chunk_sec_3",
            "security",
        ),
        (
            "q_sec_4",
            "Within what timeframe must security breaches be reported to InfoSec?",
            "Notify security team within 1 hour of identifying potential incident.",
            "security.pdf",
            4,
            "chunk_sec_4",
            "security",
        ),
        (
            "q_sec_5",
            "Why must Docker containers execute under a non-root user UID 10001?",
            "Non-root execution with UID 10001 prevents container breakout attacks.",
            "security.pdf",
            5,
            "chunk_sec_5",
            "security",
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
        for qid, q, ans, fn, pn, cid, cat in sample_records
    ]
    items.extend(
        [
            EvalDatasetItem(
                query_id=f"q_out_{i}",
                query=f"Out of corpus query {i} recipe astronomy history",
                ground_truth_answer="I cannot answer this question based on the available documentation.",
                ground_truth_citations=[],
                is_out_of_corpus=True,
                category="out_of_corpus",
            )
            for i in range(1, 4)
        ]
    )
    return EvalDataset(items=items)


def test_build_corpus_chunks_from_dataset() -> None:
    """Verify ground-truth ChunkDocument corpus generation from dataset."""
    dataset = _create_sample_eval_dataset()
    chunks = build_corpus_chunks_from_dataset(dataset)
    assert len(chunks) == 10
    sla_chunks = [c for c in chunks if c.file_name == "sla.pdf"]
    assert len(sla_chunks) == 5
    assert all(c.metadata.token_count >= 1 for c in chunks)


def test_create_calibrated_retrieval_monitor() -> None:
    """Verify calibrated hybrid RetrievalMonitor indexes corpus and retrieves relevant hits."""
    dataset = _create_sample_eval_dataset()
    chunks = build_corpus_chunks_from_dataset(dataset)
    monitor = create_calibrated_retrieval_monitor(chunks, threshold=0.75)

    hits = monitor.retrieve("SLA notice period", top_k=5)
    assert len(hits) > 0
    assert any("sla" in h.file_name for h in hits)


def test_validate_precision_at_5_success_on_sample_dataset() -> None:
    """Verify precision validation passes and achieves >= 0.75 on sample dataset."""
    dataset = _create_sample_eval_dataset()
    validator = RetrievalPrecisionValidator(min_precision_threshold=0.75)

    result = validator.validate(dataset=dataset, top_k=5)
    assert isinstance(result, RetrievalPrecisionValidationResult)
    assert result.passed is True
    assert result.measured_precision_at_5 >= 0.75
    assert result.target_threshold == 0.75
    assert result.total_queries == 13
    assert result.in_corpus_queries == 10
    assert result.out_of_corpus_queries == 3
    assert "sla" in result.category_precisions
    assert "security" in result.category_precisions
    assert result.category_precisions["sla"] >= 0.75
    assert result.category_precisions["security"] >= 0.75


def test_validate_precision_at_5_on_real_eval_dataset() -> None:
    """Verify benchmark validation against actual 52-query eval_dataset.jsonl (Phase 10.3 target)."""
    dataset = load_eval_dataset_from_jsonl()
    validator = RetrievalPrecisionValidator(min_precision_threshold=0.75)

    result = validator.validate(dataset=dataset, top_k=5)
    assert result.passed is True
    assert result.measured_precision_at_5 >= 0.75
    assert result.total_queries >= 50
    assert result.in_corpus_queries >= 40
    assert result.out_of_corpus_queries >= 10
    assert result.report.precision_threshold_passed is True


def test_validate_precision_with_report_file_output(tmp_path: Path) -> None:
    """Verify precision validator renders and writes markdown benchmark report to disk."""
    dataset = _create_sample_eval_dataset()
    out_file = tmp_path / "reports" / "retrieval_precision_report.md"
    validator = RetrievalPrecisionValidator(min_precision_threshold=0.75)

    result = validator.validate(dataset=dataset, top_k=5, output_report_path=out_file)
    assert result.passed is True
    assert out_file.is_file()
    content = out_file.read_text(encoding="utf-8")
    assert "# Retrieval & Grounding Benchmark Report" in content
    assert "retrieval_precision@5" in content


def test_validate_precision_threshold_failure() -> None:
    """Verify validator flags failure when measured precision is below target threshold."""
    dataset = _create_sample_eval_dataset()

    def failing_retriever(query: str, top_k: int) -> list[RetrievalResult]:
        return [
            RetrievalResult(
                chunk_id="unrelated_chunk",
                text="unrelated text",
                file_name="unrelated.pdf",
                page_number=99,
                relevance_score=0.9,
                retrieval_method="hybrid",
            )
        ]

    monitor = RetrievalMonitor(retriever_fn=failing_retriever)
    validator = RetrievalPrecisionValidator(
        monitor=monitor, min_precision_threshold=0.75
    )

    result = validator.validate(dataset=dataset, top_k=5)
    assert result.passed is False
    assert result.measured_precision_at_5 == 0.0


def test_validate_empty_dataset_raises_evaluation_error() -> None:
    """Verify validator raises EvaluationError when called with empty dataset."""
    validator = RetrievalPrecisionValidator()
    with pytest.raises(EvaluationError) as exc_info:
        validator.validate(dataset=EvalDataset(items=[]))
    assert exc_info.value.code == "EMPTY_EVAL_DATASET"


def test_validation_result_immutability() -> None:
    """Verify RetrievalPrecisionValidationResult enforces frozen model constraints."""
    dataset = _create_sample_eval_dataset()
    validator = RetrievalPrecisionValidator()
    result = validator.validate(dataset=dataset)

    with pytest.raises(ValueError):
        result.passed = False  # type: ignore[misc]

    with pytest.raises(ValueError):
        RetrievalPrecisionValidationResult(extra_field="invalid")  # type: ignore[call-arg]
