"""Unit tests for RetrievalMonitor service methods and per-item evaluation."""

from unittest.mock import MagicMock

import pytest

from core.exceptions import EvaluationError
from models.evaluation import (
    EvalDataset,
    EvalDatasetItem,
    EvalGroundTruthCitation,
)
from models.retrieval import RetrievalResult
from retrieval.confidence_guard import ConfidenceGuard
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


def test_monitor_init_and_threshold_defaults() -> None:
    """Verify monitor initialization and quality threshold defaults."""
    monitor = RetrievalMonitor()
    assert monitor.thresholds.min_precision_at_5 == 0.75
    assert monitor.thresholds.min_honesty_filter_precision == 0.90
    assert monitor.thresholds.max_p95_latency_ms == 3000.0


def test_retrieve_with_retriever_fn() -> None:
    """Verify retrieval using injected retriever callable."""
    hit = RetrievalResult(
        chunk_id="chunk_sla_1",
        text="SLA 30 days",
        file_name="sla.pdf",
        page_number=1,
        relevance_score=0.92,
        retrieval_method="hybrid",
    )
    mock_fn = MagicMock(return_value=[hit])
    monitor = RetrievalMonitor(retriever_fn=mock_fn)

    results = monitor.retrieve("notice period", top_k=5)
    assert len(results) == 1
    assert results[0].chunk_id == "chunk_sla_1"
    mock_fn.assert_called_once_with("notice period", 5)


def test_retrieve_with_hybrid_services_and_reranker() -> None:
    """Verify retrieval with mocked dense, sparse, rrf, and reranker services."""
    dense_hit = RetrievalResult(
        chunk_id="c1",
        text="t1",
        file_name="f1",
        page_number=1,
        relevance_score=0.8,
        retrieval_method="dense",
    )
    sparse_hit = RetrievalResult(
        chunk_id="c1",
        text="t1",
        file_name="f1",
        page_number=1,
        relevance_score=10.0,
        retrieval_method="sparse",
    )
    fused_hit = RetrievalResult(
        chunk_id="c1",
        text="t1",
        file_name="f1",
        page_number=1,
        relevance_score=0.03,
        retrieval_method="rrf",
    )
    reranked_hit = RetrievalResult(
        chunk_id="c1",
        text="t1",
        file_name="f1",
        page_number=1,
        relevance_score=0.89,
        retrieval_method="flashrank",
    )

    mock_dense = MagicMock()
    mock_dense.search.return_value = [dense_hit]
    mock_sparse = MagicMock()
    mock_sparse.search.return_value = [sparse_hit]
    mock_rrf = MagicMock()
    mock_rrf.fuse.return_value = [fused_hit]
    mock_rerank = MagicMock()
    mock_rerank.rerank.return_value = [reranked_hit]

    monitor = RetrievalMonitor(
        dense_search=mock_dense,
        sparse_search=mock_sparse,
        rrf_fusion=mock_rrf,
        reranker=mock_rerank,
    )
    hits = monitor.retrieve("test query", top_k=3)
    assert hits == [reranked_hit]


def test_retrieve_with_hybrid_services_without_reranker() -> None:
    """Verify retrieval falls back to top_k slice of fused hits if reranker is omitted."""
    fused_hits = [
        RetrievalResult(
            chunk_id=f"c{i}",
            text="t",
            file_name="f",
            page_number=1,
            relevance_score=0.1,
            retrieval_method="rrf",
        )
        for i in range(10)
    ]
    mock_dense = MagicMock(search=MagicMock(return_value=[]))
    mock_sparse = MagicMock(search=MagicMock(return_value=[]))
    mock_rrf = MagicMock(fuse=MagicMock(return_value=fused_hits))

    monitor = RetrievalMonitor(
        dense_search=mock_dense, sparse_search=mock_sparse, rrf_fusion=mock_rrf
    )
    results = monitor.retrieve("query", top_k=4)
    assert len(results) == 4


def test_retrieve_unconfigured_raises_evaluation_error() -> None:
    """Verify EvaluationError is raised if monitor has no retrieval mechanism."""
    monitor = RetrievalMonitor()
    with pytest.raises(EvaluationError) as exc_info:
        monitor.retrieve("query")
    assert exc_info.value.code == "RETRIEVER_UNCONFIGURED"


def test_evaluate_item_in_corpus_and_out_of_corpus() -> None:
    """Verify evaluate_item calculates precision, recall, and refusal correctly."""
    dataset = _create_sample_dataset()
    in_hit = RetrievalResult(
        chunk_id="chunk_sla_1",
        text="t",
        file_name="sla.pdf",
        page_number=1,
        relevance_score=0.9,
        retrieval_method="rrf",
    )
    out_hit = RetrievalResult(
        chunk_id="unrelated",
        text="t",
        file_name="other.pdf",
        page_number=1,
        relevance_score=0.1,
        retrieval_method="rrf",
    )

    def mock_retriever(query: str, top_k: int) -> list[RetrievalResult]:
        return [in_hit] if "notice" in query else [out_hit]

    monitor = RetrievalMonitor(
        retriever_fn=mock_retriever,
        confidence_guard=ConfidenceGuard(threshold=0.35),
    )

    in_res = monitor.evaluate_item(dataset.items[0], top_k=5)
    assert in_res.precision_at_k == pytest.approx(0.2)
    assert in_res.recall_at_k == 1.0
    assert in_res.reciprocal_rank == 1.0
    assert in_res.hit_at_k is True
    assert in_res.passed_confidence_guard is True
    assert in_res.is_correctly_refused is True

    out_res = monitor.evaluate_item(dataset.items[1], top_k=5)
    assert out_res.passed_confidence_guard is False
    assert out_res.is_correctly_refused is True


def test_evaluate_item_handles_exceptions() -> None:
    """Verify query exceptions are captured safely in RetrievalQueryResult."""

    def failing_retriever(query: str, top_k: int) -> list[RetrievalResult]:
        raise RuntimeError("Vector DB connection timeout")

    dataset = _create_sample_dataset()
    monitor = RetrievalMonitor(retriever_fn=failing_retriever)
    result = monitor.evaluate_item(dataset.items[0])
    assert result.error is not None
    assert "Vector DB connection timeout" in result.error
    assert result.precision_at_k == 0.0
