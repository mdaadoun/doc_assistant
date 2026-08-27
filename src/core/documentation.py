"""Documentation validation and report generation utilities."""

from pathlib import Path
from typing import Any, Final

from core.exceptions import ConfigurationError
from core.layout import get_project_root

REQUIRED_README_SECTIONS: Final[list[str]] = [
    "Quick Start",
    "System Topology & Architecture",
    "Quality Targets & Benchmark Verification",
    "API Reference & Endpoints",
    "Production Docker Deployment",
    "Resilience, Caching & Security",
]

REQUIRED_README_KEYWORDS: Final[list[str]] = [
    "make test",
    "docker-compose",
    "Qdrant",
    "rank-bm25",
    "FlashRank",
    "retrieval_precision@5",
    "faithfulness_score",
    "honesty_filter_precision",
    "SHA-256",
    "Tenacity",
]

REQUIRED_REPORT_SECTIONS: Final[list[str]] = [
    "Executive Summary & Quality Targets",
    "Dataset & Cardinality Overview",
    "Latency Distribution",
    "Category Breakdown",
]


def validate_readme_content(content: str) -> dict[str, Any]:
    """Audit README text for required sections and technical keywords."""
    missing_sections = [
        s
        for s in REQUIRED_README_SECTIONS
        if f"## {s}" not in content and s not in content
    ]
    missing_keywords = [k for k in REQUIRED_README_KEYWORDS if k not in content]
    is_valid = len(missing_sections) == 0 and len(missing_keywords) == 0
    return {
        "valid": is_valid,
        "missing_sections": missing_sections,
        "missing_keywords": missing_keywords,
        "total_sections": len(REQUIRED_README_SECTIONS),
    }


def validate_retrieval_report_content(content: str) -> dict[str, Any]:
    """Audit retrieval report markdown for mandatory benchmark sections."""
    missing_sections = [
        s
        for s in REQUIRED_REPORT_SECTIONS
        if f"## {s}" not in content and s not in content
    ]
    has_pass_badge = "PASS" in content or "✅" in content
    has_precision = "retrieval_precision@5" in content
    has_honesty = "honesty_filter_precision" in content
    is_valid = (
        len(missing_sections) == 0 and has_pass_badge and has_precision and has_honesty
    )
    return {
        "valid": is_valid,
        "missing_sections": missing_sections,
        "has_pass_badge": has_pass_badge,
        "has_precision_metric": has_precision,
        "has_honesty_metric": has_honesty,
    }


def validate_project_documentation(
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Validate presence and completeness of README.md and retrieval_report.md."""
    root = project_root or get_project_root()
    readme_path = root / "README.md"
    report_path = root / "retrieval_report.md"

    if not readme_path.is_file():
        raise ConfigurationError(
            message=f"Mandatory documentation file missing: {readme_path}",
            code="DOCS_MISSING_README",
        )
    if not report_path.is_file():
        raise ConfigurationError(
            message=f"Mandatory benchmark report missing: {report_path}",
            code="DOCS_MISSING_REPORT",
        )

    readme_audit = validate_readme_content(readme_path.read_text(encoding="utf-8"))
    report_audit = validate_retrieval_report_content(
        report_path.read_text(encoding="utf-8")
    )

    return {
        "valid": bool(readme_audit["valid"] and report_audit["valid"]),
        "readme": readme_audit,
        "retrieval_report": report_audit,
        "readme_path": str(readme_path),
        "report_path": str(report_path),
    }
