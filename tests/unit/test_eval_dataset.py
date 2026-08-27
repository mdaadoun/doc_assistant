"""Unit tests for evaluation dataset schemas, loaders, and quality validators."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from core.eval_dataset import (
    get_default_eval_dataset_path,
    load_eval_dataset_from_jsonl,
    save_eval_dataset_to_jsonl,
    validate_eval_dataset_quality,
)
from core.exceptions import IngestionError
from models.evaluation import EvalDataset, EvalDatasetItem, EvalGroundTruthCitation


def test_load_default_eval_dataset_and_validate_thresholds() -> None:
    """Verify default eval_dataset.jsonl loads correctly and satisfies thresholds."""
    default_path = get_default_eval_dataset_path()
    assert default_path.is_file()

    dataset = load_eval_dataset_from_jsonl()
    assert dataset.total_queries >= 50
    assert dataset.out_of_corpus_count >= 10
    assert dataset.in_corpus_count >= 40

    audit = validate_eval_dataset_quality(dataset, min_total=50, min_out_of_corpus=10)
    assert audit["valid"] is True
    assert len(audit["errors"]) == 0
    assert audit["total_queries"] == dataset.total_queries
    assert audit["out_of_corpus_count"] == dataset.out_of_corpus_count


def test_eval_dataset_item_immutability() -> None:
    """Verify evaluation domain models enforce frozen immutability."""
    citation = EvalGroundTruthCitation(
        file_name="test.pdf", page_number=1, chunk_id="chk-1", excerpt="text"
    )
    with pytest.raises(ValidationError):
        citation.page_number = 2

    item = EvalDatasetItem(
        query_id="eval-001",
        query="What is the SLA?",
        ground_truth_answer="30 days notice",
        ground_truth_citations=[citation],
        is_out_of_corpus=False,
        category="sla",
    )
    with pytest.raises(ValidationError):
        item.query = "Changed"


def test_validate_eval_dataset_quality_error_branches() -> None:
    """Verify quality auditor detects invalid schema states and edge cases."""
    duplicate_items = [
        EvalDatasetItem(
            query_id="eval-dup",
            query="Query 1",
            ground_truth_answer="Answer 1",
            ground_truth_citations=[
                EvalGroundTruthCitation(
                    file_name="doc.pdf", page_number=1, chunk_id="chk-1"
                )
            ],
            is_out_of_corpus=False,
        ),
        EvalDatasetItem(
            query_id="eval-dup",
            query="Query 2",
            ground_truth_answer="Answer 2",
            ground_truth_citations=[
                EvalGroundTruthCitation(
                    file_name="doc.pdf", page_number=1, chunk_id="chk-2"
                )
            ],
            is_out_of_corpus=False,
        ),
    ]
    audit_dup = validate_eval_dataset_quality(
        EvalDataset(items=duplicate_items), min_total=1, min_out_of_corpus=0
    )
    assert audit_dup["valid"] is False
    assert any("Duplicate query_id" in err for err in audit_dup["errors"])

    invalid_out_of_corpus = [
        EvalDatasetItem(
            query_id="eval-ooc-bad",
            query="Pizza recipe?",
            ground_truth_answer="I cannot answer",
            ground_truth_citations=[
                EvalGroundTruthCitation(
                    file_name="doc.pdf", page_number=1, chunk_id="chk-1"
                )
            ],
            is_out_of_corpus=True,
        )
    ]
    audit_ooc = validate_eval_dataset_quality(
        EvalDataset(items=invalid_out_of_corpus), min_total=1, min_out_of_corpus=1
    )
    assert audit_ooc["valid"] is False
    assert any(
        "should have no ground truth citations" in err for err in audit_ooc["errors"]
    )


def test_load_eval_dataset_missing_file_raises_ingestion_error(tmp_path: Path) -> None:
    """Verify IngestionError raised when loading from non-existent file path."""
    missing_file = tmp_path / "non_existent.jsonl"
    with pytest.raises(IngestionError) as exc_info:
        load_eval_dataset_from_jsonl(missing_file)
    assert exc_info.value.code == "EVAL_DATASET_NOT_FOUND"


def test_load_eval_dataset_corrupted_json_raises_ingestion_error(
    tmp_path: Path,
) -> None:
    """Verify IngestionError raised when loading corrupted JSON lines."""
    bad_file = tmp_path / "bad.jsonl"
    bad_file.write_text("INVALID_JSON_LINE\n", encoding="utf-8")
    with pytest.raises(IngestionError) as exc_info:
        load_eval_dataset_from_jsonl(bad_file)
    assert exc_info.value.code == "EVAL_DATASET_CORRUPTED"


def test_save_and_reload_eval_dataset_roundtrip(tmp_path: Path) -> None:
    """Verify saving and re-loading dataset preserves item equality."""
    dataset = load_eval_dataset_from_jsonl()
    temp_target = tmp_path / "saved_eval.jsonl"

    count = save_eval_dataset_to_jsonl(dataset, temp_target)
    assert count == dataset.total_queries
    assert temp_target.is_file()

    reloaded = load_eval_dataset_from_jsonl(temp_target)
    assert reloaded.total_queries == dataset.total_queries
    assert reloaded.items[0].query_id == dataset.items[0].query_id
    assert reloaded.items[0].query == dataset.items[0].query
