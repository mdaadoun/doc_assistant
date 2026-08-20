"""Dataset loader and quality validation utilities for evaluation benchmarks."""

import json
from pathlib import Path
from typing import Any

from core.exceptions import IngestionError
from models.evaluation import EvalDataset, EvalDatasetItem


def get_default_eval_dataset_path(base_dir: Path | None = None) -> Path:
    """Return default filesystem path to evaluation dataset JSONL."""
    root = base_dir or Path(__file__).resolve().parent.parent.parent
    return root / "data" / "eval_dataset.jsonl"


def load_eval_dataset_from_jsonl(
    file_path: Path | str | None = None,
) -> EvalDataset:
    """Load and validate evaluation dataset from a JSONL file.

    Raises IngestionError on missing file, corrupted JSON, or schema mismatch.
    """
    path = Path(file_path) if file_path else get_default_eval_dataset_path()
    if not path.is_file():
        raise IngestionError(
            message=f"Evaluation dataset file not found at: {path}",
            code="EVAL_DATASET_NOT_FOUND",
            details={"path": str(path)},
        )

    items: list[EvalDatasetItem] = []
    try:
        with open(path, encoding="utf-8") as f:
            for line_idx, line in enumerate(f, start=1):
                clean_line = line.strip()
                if not clean_line:
                    continue
                try:
                    payload = json.loads(clean_line)
                    item = EvalDatasetItem.model_validate(payload)
                    items.append(item)
                except (json.JSONDecodeError, ValueError) as exc:
                    raise IngestionError(
                        message=f"Malformed evaluation record at line {line_idx}: {exc}",
                        code="EVAL_DATASET_CORRUPTED",
                        details={
                            "path": str(path),
                            "line": line_idx,
                            "error": str(exc),
                        },
                    ) from exc
    except OSError as exc:
        raise IngestionError(
            message=f"Failed to read evaluation dataset file: {exc}",
            code="EVAL_DATASET_READ_ERROR",
            details={"path": str(path), "error": str(exc)},
        ) from exc

    return EvalDataset(items=items)


def save_eval_dataset_to_jsonl(dataset: EvalDataset, file_path: Path | str) -> int:
    """Save an EvalDataset instance to a JSONL file.

    Returns the count of serialized items.
    """
    path = Path(file_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for item in dataset.items:
                f.write(item.model_dump_json() + "\n")
        return len(dataset.items)
    except OSError as exc:
        raise IngestionError(
            message=f"Failed to write evaluation dataset file: {exc}",
            code="EVAL_DATASET_WRITE_ERROR",
            details={"path": str(path), "error": str(exc)},
        ) from exc


def validate_eval_dataset_quality(
    dataset: EvalDataset,
    min_total: int = 50,
    min_out_of_corpus: int = 10,
) -> dict[str, Any]:
    """Validate dataset cardinality, boundary criteria, and schema integrity."""
    errors: list[str] = []
    seen_ids: set[str] = set()

    for idx, item in enumerate(dataset.items):
        if item.query_id in seen_ids:
            errors.append(f"Duplicate query_id '{item.query_id}' at index {idx}")
        seen_ids.add(item.query_id)

        if not item.query.strip():
            errors.append(f"Empty query at index {idx} (id: {item.query_id})")
        if not item.ground_truth_answer.strip():
            errors.append(
                f"Empty ground_truth_answer at index {idx} (id: {item.query_id})"
            )

        if item.is_out_of_corpus:
            if len(item.ground_truth_citations) > 0:
                errors.append(
                    f"Out-of-corpus query '{item.query_id}' should have no ground truth citations"
                )
        else:
            if len(item.ground_truth_citations) == 0:
                errors.append(
                    f"In-corpus query '{item.query_id}' must have at least 1 ground truth citation"
                )

    if dataset.total_queries < min_total:
        errors.append(
            f"Dataset total queries ({dataset.total_queries}) below threshold ({min_total})"
        )
    if dataset.out_of_corpus_count < min_out_of_corpus:
        errors.append(
            f"Out-of-corpus queries ({dataset.out_of_corpus_count}) below threshold ({min_out_of_corpus})"
        )

    is_valid = len(errors) == 0
    return {
        "valid": is_valid,
        "total_queries": dataset.total_queries,
        "in_corpus_count": dataset.in_corpus_count,
        "out_of_corpus_count": dataset.out_of_corpus_count,
        "errors": errors,
    }
