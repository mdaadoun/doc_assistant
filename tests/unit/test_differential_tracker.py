"""Unit tests for differential update tracker and differential ingestion workflow."""

from pathlib import Path

import pytest

from core.exceptions import IngestionError
from ingestion.facade import IngestionFacade
from ingestion.tracker import DifferentialTracker
from models.differential import StateManifest


def test_compute_file_hash_success(tmp_path: Path) -> None:
    """Verify SHA-256 computation on local text file."""
    file_path = tmp_path / "sample.md"
    file_path.write_text("# Title\nSample content", encoding="utf-8")

    hash_val = DifferentialTracker.compute_file_hash(file_path)
    assert len(hash_val) == 64
    assert isinstance(hash_val, str)


def test_compute_file_hash_nonexistent_file(tmp_path: Path) -> None:
    """Verify error raised when computing hash for non-existent file."""
    missing = tmp_path / "missing.md"
    with pytest.raises(IngestionError) as exc_info:
        DifferentialTracker.compute_file_hash(missing)
    assert exc_info.value.code == "FILE_NOT_FOUND"


def test_scan_new_files(tmp_path: Path) -> None:
    """Verify fresh scan categorizes files as new_files."""
    f1 = tmp_path / "doc1.md"
    f2 = tmp_path / "doc2.md"
    f1.write_text("# Doc 1\nContent 1", encoding="utf-8")
    f2.write_text("# Doc 2\nContent 2", encoding="utf-8")

    tracker = DifferentialTracker()
    delta = tracker.scan([f1, f2])

    assert delta.has_changes is True
    assert len(delta.new_files) == 2
    assert len(delta.changed_files) == 0
    assert len(delta.deleted_files) == 0
    assert len(delta.unchanged_files) == 0
    assert len(delta.files_to_process) == 2


def test_scan_unchanged_and_changed_files(tmp_path: Path) -> None:
    """Verify scan identifies unchanged and modified files accurately."""
    f1 = tmp_path / "doc1.md"
    f2 = tmp_path / "doc2.md"
    f1.write_text("# Doc 1\nContent 1", encoding="utf-8")
    f2.write_text("# Doc 2\nContent 2", encoding="utf-8")

    tracker = DifferentialTracker()
    tracker.update_file_state(f1)
    tracker.update_file_state(f2)

    # Re-scan without changes
    delta1 = tracker.scan([f1, f2])
    assert delta1.has_changes is False
    assert len(delta1.unchanged_files) == 2
    assert len(delta1.files_to_process) == 0

    # Modify f1 content
    f1.write_text("# Doc 1 Modified\nUpdated Content 1", encoding="utf-8")
    delta2 = tracker.scan([f1, f2])
    assert delta2.has_changes is True
    assert len(delta2.changed_files) == 1
    assert str(f1.resolve()) in delta2.changed_files
    assert len(delta2.unchanged_files) == 1
    assert str(f2.resolve()) in delta2.unchanged_files


def test_scan_deleted_files_and_sync(tmp_path: Path) -> None:
    """Verify deleted files detection and manifest synchronization."""
    f1 = tmp_path / "doc1.md"
    f2 = tmp_path / "doc2.md"
    f1.write_text("# Doc 1", encoding="utf-8")
    f2.write_text("# Doc 2", encoding="utf-8")

    tracker = DifferentialTracker()
    tracker.update_file_state(f1)
    tracker.update_file_state(f2)

    # Delete f2 from disk
    f2.unlink()

    delta = tracker.scan([f1])
    assert str(f2.resolve()) in delta.deleted_files
    assert len(delta.deleted_files) == 1

    # Sync delta to purge deleted state
    tracker.sync_delta(delta)
    assert str(f2.resolve()) not in tracker.manifest.files


def test_manifest_persistence_save_load(tmp_path: Path) -> None:
    """Verify saving and loading manifest file from disk."""
    f1 = tmp_path / "doc1.md"
    f1.write_text("# Persistence test", encoding="utf-8")

    manifest_file = tmp_path / "manifest.json"
    tracker = DifferentialTracker(manifest_path=manifest_file)
    tracker.update_file_state(f1, chunk_ids=["c1", "c2"])
    saved_path = tracker.save_manifest()

    assert saved_path.exists()

    # Load in new tracker instance
    tracker2 = DifferentialTracker(manifest_path=manifest_file)
    assert isinstance(tracker2.manifest, StateManifest)
    assert str(f1.resolve()) in tracker2.manifest.files
    loaded_state = tracker2.manifest.files[str(f1.resolve())]
    assert loaded_state.chunk_ids == ["c1", "c2"]


def test_load_manifest_error_cases(tmp_path: Path) -> None:
    """Verify exceptions on non-existent or corrupted manifest loading."""
    tracker = DifferentialTracker()

    with pytest.raises(IngestionError) as exc1:
        tracker.load_manifest(tmp_path / "nonexistent.json")
    assert exc1.value.code == "MANIFEST_NOT_FOUND"

    bad_json = tmp_path / "corrupt.json"
    bad_json.write_text("{ invalid json: ", encoding="utf-8")
    with pytest.raises(IngestionError) as exc2:
        tracker.load_manifest(bad_json)
    assert exc2.value.code == "INVALID_MANIFEST"


def test_ingest_differential_facade_workflow(tmp_path: Path) -> None:
    """Verify end-to-end differential ingestion workflow via IngestionFacade."""
    doc_dir = tmp_path / "docs"
    doc_dir.mkdir()
    f1 = doc_dir / "guide.md"
    f2 = doc_dir / "policy.md"
    f1.write_text("# Corporate Guide\nSection 1 text", encoding="utf-8")
    f2.write_text("# Policy Manual\nSection 2 text", encoding="utf-8")

    manifest_file = tmp_path / "manifest.json"
    tracker = DifferentialTracker(manifest_path=manifest_file)
    facade = IngestionFacade(tracker=tracker)

    # Initial differential ingestion
    res1 = facade.ingest_differential(doc_dir)
    assert res1.processed_count == 2
    assert len(res1.chunks) > 0
    assert len(res1.delta.new_files) == 2

    # Second differential ingestion without modifications
    res2 = facade.ingest_differential(doc_dir)
    assert res2.processed_count == 0
    assert len(res2.chunks) == 0
    assert res2.delta.has_changes is False

    # Modify one file and re-ingest
    f1.write_text(
        "# Corporate Guide Updated\nModified Section 1 text", encoding="utf-8"
    )
    res3 = facade.ingest_differential(doc_dir)
    assert res3.processed_count == 1
    assert len(res3.chunks) > 0
    assert len(res3.delta.changed_files) == 1
    assert str(f1.resolve()) in res3.delta.changed_files
