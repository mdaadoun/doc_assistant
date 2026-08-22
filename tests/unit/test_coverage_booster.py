"""Unit and integration tests ensuring comprehensive test coverage (>= 80%)."""

from collections.abc import AsyncGenerator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from api.services.chat_service import ChatService
from clients.gemini_embedding import GeminiEmbeddingAdapter
from core.eval_dataset import (
    load_eval_dataset_from_jsonl,
    save_eval_dataset_to_jsonl,
    validate_eval_dataset_quality,
)
from core.exceptions import ConfigurationError
from core.logger import get_logger, setup_logger
from generation.citations import (
    CitationExtractor,
    CitationValidator,
    RawCitation,
)
from generation.sse import SSEResponseHandler
from models.chat import ChatRequest
from models.evaluation import (
    EvalDataset,
    EvalDatasetItem,
    EvalGroundTruthCitation,
)
from models.retrieval import RetrievalResult


def test_core_logger_configuration_and_retrieval() -> None:
    """Verify structured logger initialization and logger instance acquisition."""
    setup_logger(log_level="DEBUG")
    log = get_logger("test_module")
    assert log is not None


@pytest.mark.asyncio
async def test_chat_service_end_to_end_grounded_stream() -> None:
    """Verify full ChatService execution path with mock search, reranking, and grounded stream."""
    dense_search = MagicMock()
    sparse_search = MagicMock()
    rrf_fusion = MagicMock()
    reranker = MagicMock()
    confidence_guard = MagicMock()
    grounded_gen = MagicMock()

    sample_hit = RetrievalResult(
        chunk_id="c1",
        text="Sample context content [Doc: test.pdf | Page: 1].",
        file_name="test.pdf",
        page_number=1,
        relevance_score=0.92,
        retrieval_method="hybrid",
    )

    dense_search.search.return_value = [sample_hit]
    sparse_search.search.return_value = [sample_hit]
    rrf_fusion.fuse.return_value = [sample_hit]
    reranker.rerank.return_value = [sample_hit]

    decision_mock = MagicMock()
    decision_mock.passed = True
    decision_mock.top_score = 0.92
    decision_mock.filtered_hits = [sample_hit]
    confidence_guard.evaluate.return_value = decision_mock

    async def mock_token_stream(
        query: str, contexts: list[RetrievalResult]
    ) -> AsyncGenerator[str, None]:
        yield "The answer "
        yield "is grounded."

    grounded_gen.generate_stream = mock_token_stream

    service = ChatService(
        dense_search=dense_search,
        sparse_search=sparse_search,
        rrf_fusion=rrf_fusion,
        reranker=reranker,
        confidence_guard=confidence_guard,
        grounded_generator=grounded_gen,
        sse_handler=SSEResponseHandler(),
    )

    req = ChatRequest(
        query="What is the policy?",
        conversation_id="conv-123",
        top_k=5,
    )

    events: list[str] = []
    async for event in service.stream_chat(req):
        events.append(event)

    assert len(events) > 0
    assert any("metadata" in e for e in events)
    assert any("done" in e for e in events)


@pytest.mark.asyncio
async def test_chat_service_without_generator_fallback() -> None:
    """Verify ChatService fallback when grounded generator is not configured."""
    confidence_guard = MagicMock()
    decision_mock = MagicMock()
    decision_mock.passed = True
    decision_mock.top_score = 0.90
    decision_mock.filtered_hits = [
        RetrievalResult(
            chunk_id="c1",
            text="Context",
            file_name="doc.pdf",
            page_number=1,
            relevance_score=0.90,
            retrieval_method="dense",
        )
    ]
    confidence_guard.evaluate.return_value = decision_mock

    service = ChatService(
        confidence_guard=confidence_guard,
        grounded_generator=None,
    )

    req = ChatRequest(query="Test", conversation_id="conv-1")
    events = [e async for e in service.stream_chat(req)]
    assert len(events) > 0


def test_gemini_embedding_client_configuration_and_errors() -> None:
    """Verify GeminiEmbeddingAdapter handles missing API keys and error conditions."""
    with patch("clients.gemini_embedding.get_settings") as mock_settings:
        mock_settings.return_value.gemini_api_key = ""
        with pytest.raises(ConfigurationError):
            GeminiEmbeddingAdapter(api_key="")


def test_eval_dataset_save_and_validation_edge_cases(tmp_path: Path) -> None:
    """Verify dataset quality validation and file serialization error handling."""
    dest_path = tmp_path / "saved_eval.jsonl"
    dataset = load_eval_dataset_from_jsonl()
    count = save_eval_dataset_to_jsonl(dataset, dest_path)
    assert count == len(dataset.items)
    assert dest_path.is_file()

    # Empty query or missing citations validation
    bad_items = [
        EvalDatasetItem(
            query_id="bad_1",
            query="   ",
            ground_truth_answer="Ans",
            ground_truth_citations=[],
            is_out_of_corpus=False,
        ),
        EvalDatasetItem(
            query_id="bad_1",  # Duplicate ID
            query="Valid query",
            ground_truth_answer="  ",
            ground_truth_citations=[
                EvalGroundTruthCitation(file_name="f", page_number=1, chunk_id="c")
            ],
            is_out_of_corpus=True,  # OOC with citations
        ),
    ]
    val_report = validate_eval_dataset_quality(EvalDataset(items=bad_items))
    assert val_report["valid"] is False
    assert len(val_report["errors"]) > 0


def test_citation_extractor_regex_fallback() -> None:
    """Verify CitationExtractor regex parser on varied format tags."""
    text = "Here is an answer [Doc: sample_policy.pdf | Page: 3] with facts."
    raw = CitationExtractor.extract_raw(text)
    assert len(raw) == 1
    assert raw[0].file_name == "sample_policy.pdf"
    assert raw[0].page_number == 3

    # Direct RawCitation
    tag = RawCitation(file_name="test.pdf", page_number=2)
    assert tag.file_name == "test.pdf"

    # CitationValidator
    res = CitationValidator.validate(
        text,
        contexts=[
            RetrievalResult(
                chunk_id="c1",
                text="Sample text",
                file_name="sample_policy.pdf",
                page_number=3,
                relevance_score=0.9,
                retrieval_method="dense",
            )
        ],
    )
    assert res.is_valid is True
    assert res.citation_accuracy == 1.0
    assert len(res.valid_citations) == 1
