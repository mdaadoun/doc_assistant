"""Unit tests for RAGAS faithfulness framework and FaithfulnessValidator (>= 0.85)."""

from pathlib import Path

import pytest

from core.eval_dataset import load_eval_dataset_from_jsonl
from core.exceptions import EvaluationError
from generation.faithfulness import RAGASFaithfulnessEvaluator
from generation.faithfulness_validator import FaithfulnessValidator
from generation.statement_extractor import StatementExtractor
from models.evaluation import (
    EvalDataset,
    EvalDatasetItem,
    EvalGroundTruthCitation,
)
from models.faithfulness import (
    FaithfulnessQueryResult,
    FaithfulnessValidationResult,
    StatementVerification,
)


def _create_sample_eval_dataset() -> EvalDataset:
    """Create a sample evaluation dataset for faithfulness tests."""
    items = [
        EvalDatasetItem(
            query_id="eval-test-1",
            query="What is the notice period for contract termination?",
            ground_truth_answer="The standard SLA requires a written notice period of 30 calendar days [Doc: sla.pdf | Page: 1].",
            ground_truth_citations=[
                EvalGroundTruthCitation(
                    file_name="sla.pdf",
                    page_number=1,
                    chunk_id="chunk-1",
                    excerpt="Either party may terminate this agreement by providing a written notice period of no less than 30 calendar days.",
                )
            ],
            is_out_of_corpus=False,
            category="sla",
        ),
        EvalDatasetItem(
            query_id="eval-test-2",
            query="What is the guaranteed monthly uptime?",
            ground_truth_answer="The SLA guarantees 99.9% monthly uptime availability [Doc: sla.pdf | Page: 2].",
            ground_truth_citations=[
                EvalGroundTruthCitation(
                    file_name="sla.pdf",
                    page_number=2,
                    chunk_id="chunk-2",
                    excerpt="The provider guarantees a monthly uptime availability level of 99.9%.",
                )
            ],
            is_out_of_corpus=False,
            category="sla",
        ),
        EvalDatasetItem(
            query_id="eval-test-3",
            query="What is the capital of Mars?",
            ground_truth_answer="I cannot answer this question based on the available documentation.",
            ground_truth_citations=[],
            is_out_of_corpus=True,
            category="out_of_corpus",
        ),
    ]
    return EvalDataset(items=items)


def test_statement_extractor_basic_and_citations() -> None:
    """Verify StatementExtractor strips citations and extracts atomic sentences."""
    text = "The SLA requires 30 days notice [Doc: sla.pdf | Page: 14]. Emergency termination is immediate [Doc: sec.pdf | Page: 3]."
    statements = StatementExtractor.extract_statements(text)
    assert len(statements) == 2
    assert "Doc:" not in statements[0]
    assert "30 days notice" in statements[0]
    assert "Emergency termination is immediate" in statements[1]


def test_statement_extractor_refusal_and_empty() -> None:
    """Verify StatementExtractor handles refusal strings and empty inputs."""
    refusal = "I cannot answer this question based on the available documentation."
    stmts = StatementExtractor.extract_statements(refusal)
    assert len(stmts) == 1
    assert "cannot answer this question" in stmts[0]

    assert StatementExtractor.extract_statements("") == []
    assert StatementExtractor.extract_statements("   ") == []


def test_statement_extractor_preserves_numbers_and_decimals() -> None:
    """Verify StatementExtractor does not split inside numbers, decimals, or currency."""
    text = "Availability is 99.9% monthly. The setup fee is $5,000 per tenant."
    stmts = StatementExtractor.extract_statements(text)
    assert len(stmts) == 2
    assert "99.9%" in stmts[0]
    assert "$5,000" in stmts[1]


def test_ragas_evaluator_statement_grounded() -> None:
    """Verify RAGASFaithfulnessEvaluator verifies a statement present in context."""
    statement = "The standard SLA requires a written notice period of 30 calendar days."
    contexts = [
        "Either party may terminate this agreement by providing a written notice period of no less than 30 calendar days."
    ]
    res = RAGASFaithfulnessEvaluator.verify_statement(statement, contexts)
    assert isinstance(res, StatementVerification)
    assert res.is_faithful is True
    assert res.supporting_chunk_id == "ctx-1"
    assert "30" in res.matched_keywords or "calendar" in res.matched_keywords


def test_ragas_evaluator_statement_ungrounded() -> None:
    """Verify RAGASFaithfulnessEvaluator flags ungrounded statements as unfaithful."""
    statement = "The termination notice period is 120 business days."
    contexts = ["All employees must submit expense reports within 30 days."]
    res = RAGASFaithfulnessEvaluator.verify_statement(statement, contexts)
    assert res.is_faithful is False
    assert res.supporting_chunk_id is None


def test_ragas_evaluator_refusal_handling() -> None:
    """Verify refusal verification behavior on out-of-corpus vs in-corpus queries."""
    refusal = "I cannot answer this question based on the available documentation."
    res_out = RAGASFaithfulnessEvaluator.verify_statement(
        refusal, contexts=[], is_out_of_corpus=True
    )
    assert res_out.is_faithful is True

    res_in = RAGASFaithfulnessEvaluator.verify_statement(
        refusal, contexts=["Clear answer is present here."], is_out_of_corpus=False
    )
    assert res_in.is_faithful is False


def test_ragas_evaluator_evaluate_answer_perfect_faithfulness() -> None:
    """Verify evaluate_answer calculates faithfulness_score = 1.0 on fully grounded answers."""
    query = "What is the notice period?"
    answer = "The notice period is 30 calendar days [Doc: sla.pdf | Page: 1]."
    contexts = [{"chunk_id": "c1", "text": "Notice period is 30 calendar days."}]
    res = RAGASFaithfulnessEvaluator.evaluate_answer(
        query=query, answer=answer, contexts=contexts
    )
    assert isinstance(res, FaithfulnessQueryResult)
    assert res.faithfulness_score == 1.0
    assert res.is_faithful is True
    assert res.verified_statements_count == 1
    assert res.total_statements_count == 1


def test_ragas_evaluator_evaluate_answer_partial_faithfulness() -> None:
    """Verify evaluate_answer computes fractional faithfulness on mixed claims."""
    query = "What are the terms?"
    answer = "Notice period is 30 calendar days. Monthly penalty fee is 99%."
    contexts = [{"chunk_id": "c1", "text": "Notice period is 30 calendar days."}]
    res = RAGASFaithfulnessEvaluator.evaluate_answer(
        query=query, answer=answer, contexts=contexts, min_threshold=0.85
    )
    assert res.faithfulness_score == 0.50
    assert res.is_faithful is False
    assert res.verified_statements_count == 1
    assert res.total_statements_count == 2


def test_validate_faithfulness_sample_dataset() -> None:
    """Verify FaithfulnessValidator runs and passes on sample dataset with >= 0.85."""
    dataset = _create_sample_eval_dataset()
    validator = FaithfulnessValidator(min_faithfulness_threshold=0.85)

    result = validator.validate(dataset=dataset)
    assert isinstance(result, FaithfulnessValidationResult)
    assert result.passed is True
    assert result.mean_faithfulness_score >= 0.85
    assert result.target_threshold == 0.85
    assert result.total_queries == 3
    assert result.in_corpus_queries == 2
    assert result.out_of_corpus_queries == 1
    assert "sla" in result.category_scores
    assert result.category_scores["sla"] >= 0.85


def test_validate_faithfulness_real_eval_dataset() -> None:
    """Verify FaithfulnessValidator passes on real data/eval_dataset.jsonl (Phase 10.4 target)."""
    dataset = load_eval_dataset_from_jsonl()
    validator = FaithfulnessValidator(min_faithfulness_threshold=0.85)

    result = validator.validate(dataset=dataset)
    assert result.passed is True
    assert result.mean_faithfulness_score >= 0.85
    assert result.total_queries >= 50
    assert result.in_corpus_queries >= 40
    assert result.out_of_corpus_queries >= 10


def test_validate_faithfulness_report_generation(tmp_path: Path) -> None:
    """Verify FaithfulnessValidator writes markdown benchmark report to disk."""
    dataset = _create_sample_eval_dataset()
    report_file = tmp_path / "reports" / "faithfulness_report.md"
    validator = FaithfulnessValidator(min_faithfulness_threshold=0.85)

    result = validator.validate(dataset=dataset, output_report_path=report_file)
    assert result.passed is True
    assert report_file.is_file()
    content = report_file.read_text(encoding="utf-8")
    assert "# RAGAS Faithfulness Benchmark Report" in content
    assert "faithfulness_score" in content
    assert "Executive Summary" in content


def test_validate_empty_dataset_raises_evaluation_error() -> None:
    """Verify FaithfulnessValidator raises EvaluationError on empty dataset."""
    validator = FaithfulnessValidator()
    with pytest.raises(EvaluationError) as exc_info:
        validator.validate(dataset=EvalDataset(items=[]))
    assert exc_info.value.code == "EMPTY_EVAL_DATASET"


def test_faithfulness_models_immutability() -> None:
    """Verify faithfulness models enforce frozen immutability and forbid extra fields."""
    verif = StatementVerification(
        statement="Test claim", is_faithful=True, reason="Matched"
    )
    with pytest.raises(ValueError):
        verif.is_faithful = False  # type: ignore[misc]

    with pytest.raises(ValueError):
        StatementVerification(
            statement="Test",
            is_faithful=True,
            extra_field="bad",  # type: ignore[call-arg]
        )
