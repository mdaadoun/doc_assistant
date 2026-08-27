"""Unit tests for README and retrieval report documentation validation."""

from pathlib import Path

import pytest

from core.documentation import (
    REQUIRED_README_KEYWORDS,
    REQUIRED_README_SECTIONS,
    REQUIRED_REPORT_SECTIONS,
    validate_project_documentation,
    validate_readme_content,
    validate_retrieval_report_content,
)
from core.exceptions import ConfigurationError


def test_required_documentation_constants() -> None:
    """Verify required documentation constants contain all mandatory headers."""
    assert len(REQUIRED_README_SECTIONS) >= 5
    assert "Quick Start" in REQUIRED_README_SECTIONS
    assert "System Topology & Architecture" in REQUIRED_README_SECTIONS
    assert "retrieval_precision@5" in REQUIRED_README_KEYWORDS
    assert "Executive Summary & Quality Targets" in REQUIRED_REPORT_SECTIONS


def test_validate_readme_content_valid() -> None:
    """Verify validate_readme_content passes on comprehensive valid text."""
    sample = """
    # Doc Assistant
    ## Quick Start
    make test and docker-compose
    ## System Topology & Architecture
    Uses Qdrant and rank-bm25 and FlashRank
    ## Quality Targets & Benchmark Verification
    retrieval_precision@5, faithfulness_score, honesty_filter_precision
    ## API Reference & Endpoints
    Endpoints /api/v1/chat
    ## Production Docker Deployment
    Docker container details
    ## Resilience, Caching & Security
    SHA-256 and Tenacity
    """
    res = validate_readme_content(sample)
    assert res["valid"] is True
    assert len(res["missing_sections"]) == 0
    assert len(res["missing_keywords"]) == 0


def test_validate_readme_content_missing_sections_and_keywords() -> None:
    """Verify validate_readme_content detects missing sections and keywords."""
    sample = "# Minimal README\n## Quick Start\nJust run python main.py"
    res = validate_readme_content(sample)
    assert res["valid"] is False
    assert "System Topology & Architecture" in res["missing_sections"]
    assert "Qdrant" in res["missing_keywords"]


def test_validate_retrieval_report_content_valid() -> None:
    """Verify validate_retrieval_report_content passes on valid report text."""
    sample = """
    # Benchmark Report
    STATUS: ✅ PASS
    ## Executive Summary & Quality Targets
    | Metric | Measured |
    | retrieval_precision@5 | 1.00 |
    | honesty_filter_precision | 0.90 |
    ## Dataset & Cardinality Overview
    Total: 52
    ## Latency Distribution
    p95: 0.7 ms
    ## Category Breakdown
    SLA, Legal, HR
    """
    res = validate_retrieval_report_content(sample)
    assert res["valid"] is True
    assert len(res["missing_sections"]) == 0
    assert res["has_pass_badge"] is True


def test_validate_retrieval_report_content_missing() -> None:
    """Verify validate_retrieval_report_content detects missing benchmark parts."""
    sample = "# Incomplete Report\nNo tables here."
    res = validate_retrieval_report_content(sample)
    assert res["valid"] is False
    assert "Executive Summary & Quality Targets" in res["missing_sections"]


def test_validate_project_documentation_missing_readme(tmp_path: Path) -> None:
    """Verify validate_project_documentation raises ConfigurationError if README is missing."""
    with pytest.raises(
        ConfigurationError, match="Mandatory documentation file missing"
    ):
        validate_project_documentation(project_root=tmp_path)


def test_validate_project_documentation_missing_report(tmp_path: Path) -> None:
    """Verify validate_project_documentation raises ConfigurationError if report is missing."""
    (tmp_path / "README.md").write_text("# Readme", encoding="utf-8")
    with pytest.raises(ConfigurationError, match="Mandatory benchmark report missing"):
        validate_project_documentation(project_root=tmp_path)
