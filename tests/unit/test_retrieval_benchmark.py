"""Unit tests for RetrievalMonitor dataset benchmarking, thresholds, and immutability."""

from pathlib import Path

import pytest

from core.eval_dataset import save_eval_dataset_to_jsonl
from core.exceptions import EvaluationError
from models.evaluation import (
    EvalDataset,
    EvalDatasetItem,
    EvalGroundTruthCitation,
    RetrievalBenchmarkReport,
    RetrievalMetricThresholds,
    RetrievalQueryResult,
)
from models.retrieval import RetrievalResult
from retrieval.monitor import RetrievalMonitor


def _create_sample_dataset() -> EvalDataset:
    """Construct a minimal dataset with in-corpus and out-of-corpus items."""
    in_item = EvalDatasetItem(
        query_id="q_in_1",
        query="What is the notice period?",
        ground_truth_answer="30 calendar days.",
        ground_truth_citations=[
            EvalGroundTruthCitation(
                file_name="sla.pdf", page_number=1, chunk_id="chunk_sla_1"
            )
        ],
        is_out_of_corpus=False,
        category="sla",
    )
    out_item = EvalDatasetItem(
        query_id="q_out_1",
        query="What is the recipe for chocolate cake?",
        ground_truth_answer="I cannot answer this question based on the available documentation.",
        ground_truth_citations=[],
        is_out_of_corpus=True,
        category="out_of_corpus",
    )
    return EvalDataset(items=[in_item, out_item])


def test_run_benchmark_and_generate_report(tmp_path: Path) -> None:
    """Verify full benchmark execution, threshold validation, and report rendering."""
    dataset = _create_sample_dataset()
    dataset_file = tmp_path / "eval.jsonl"
    save_eval_dataset_to_jsonl(dataset, dataset_file)

    hit = RetrievalResult(
        chunk_id="chunk_sla_1",
        text="t",
        file_name="sla.pdf",
        page_number=1,
        relevance_score=0.85,
        retrieval_method="hybrid",
    )
    monitor = RetrievalMonitor(
        retriever_fn=lambda q, k: [hit] if "notice" in q else [],
        thresholds=RetrievalMetricThresholds(
            min_precision_at_5=0.2, min_honesty_filter_precision=0.9
        ),
    )

    report = monitor.run_benchmark(dataset_path=dataset_file, top_k=5)
    assert isinstance(report, RetrievalBenchmarkReport)
    assert report.total_queries == 2
    assert report.in_corpus_queries == 1
    assert report.out_of_corpus_queries == 1
    assert report.precision_threshold_passed is True
    assert report.honesty_threshold_passed is True
    assert report.all_passed is True

    out_md = tmp_path / "benchmark_report.md"
    rendered = monitor.generate_report(report, output_path=out_md)
    assert out_md.is_file()
    assert "# Retrieval & Grounding Benchmark Report" in rendered


def test_run_benchmark_empty_dataset_raises() -> None:
    """Verify running benchmark on empty dataset raises EvaluationError."""
    monitor = RetrievalMonitor(retriever_fn=lambda q, k: [])
    with pytest.raises(EvaluationError) as exc_info:
        monitor.run_benchmark(dataset=EvalDataset(items=[]))
    assert exc_info.value.code == "EMPTY_EVAL_DATASET"


def test_evaluation_domain_models_immutability() -> None:
    """Verify evaluation domain models enforce frozen immutability and forbid extra fields."""
    res = RetrievalQueryResult(
        query_id="q1",
        query="test",
        category="sla",
        is_out_of_corpus=False,
    )
    with pytest.raises(ValueError):
        res.query_id = "modified"

    with pytest.raises(ValueError):
        RetrievalMetricThresholds(extra_field="invalid")  # type: ignore[call-arg]
