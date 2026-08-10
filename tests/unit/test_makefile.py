"""Unit tests for Makefile dev shortcuts and structure validation."""

from pathlib import Path

from core.makefile import (
    REQUIRED_MAKEFILE_TARGETS,
    parse_makefile_targets,
    validate_makefile,
)


def test_makefile_exists_and_valid() -> None:
    """Verify Makefile exists and contains all required developer targets."""
    root = Path(__file__).resolve().parent.parent.parent
    res = validate_makefile(root)
    assert res["valid"] is True
    assert res["has_phony"] is True
    assert res["missing_targets"] == []


def test_parse_makefile_targets() -> None:
    """Verify target parser extracts mandatory targets from Makefile."""
    root = Path(__file__).resolve().parent.parent.parent
    targets = parse_makefile_targets(root)
    for required in REQUIRED_MAKEFILE_TARGETS:
        assert required in targets


def test_validate_makefile_missing_file(tmp_path: Path) -> None:
    """Verify validation result when Makefile is absent."""
    res = validate_makefile(tmp_path)
    assert res["valid"] is False
    assert res["error"] == "Makefile not found"
    assert res["missing_targets"] == REQUIRED_MAKEFILE_TARGETS


def test_validate_makefile_missing_targets(tmp_path: Path) -> None:
    """Verify validation fails when mandatory targets are missing from Makefile."""
    partial_makefile = tmp_path / "Makefile"
    partial_makefile.write_text(".PHONY: help\nhelp:\n\t@echo help\n", encoding="utf-8")
    res = validate_makefile(tmp_path)
    assert res["valid"] is False
    assert "install" in res["missing_targets"]
