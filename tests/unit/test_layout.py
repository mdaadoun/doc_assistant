"""Unit tests for modular package layout validation and imports."""

import importlib
from pathlib import Path

from core.layout import (
    REQUIRED_DIRECTORIES,
    REQUIRED_PACKAGES,
    get_project_root,
    validate_package_layout,
)


def test_required_package_constants() -> None:
    """Verify REQUIRED_PACKAGES contains all expected core modules."""
    expected = {
        "api",
        "retrieval",
        "generation",
        "ingestion",
        "clients",
        "models",
        "core",
        "cache",
    }
    assert set(REQUIRED_PACKAGES) == expected


def test_required_directory_constants() -> None:
    """Verify REQUIRED_DIRECTORIES contains top-level structural paths."""
    expected = {"src", "frontend", "tests"}
    assert set(REQUIRED_DIRECTORIES) == expected


def test_get_project_root() -> None:
    """Verify project root path exists and contains pyproject.toml."""
    root = get_project_root()
    assert root.is_dir()
    assert (root / "pyproject.toml").is_file()


def test_validate_package_layout_success() -> None:
    """Verify validate_package_layout reports complete and valid structure."""
    report = validate_package_layout()
    assert report["status"] == "VALID"
    assert report["is_complete"] is True
    assert len(report["missing_packages"]) == 0
    assert len(report["missing_directories"]) == 0
    assert all(report["packages"].values())
    assert all(report["directories"].values())


def test_validate_package_layout_missing(tmp_path: Path) -> None:
    """Verify validation detects missing packages and directories in mock path."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "core").mkdir()
    (tmp_path / "src" / "core" / "__init__.py").touch()

    report = validate_package_layout(base_dir=tmp_path)
    assert report["status"] == "INVALID"
    assert report["is_complete"] is False
    assert "api" in report["missing_packages"]
    assert "frontend" in report["missing_directories"]


def test_package_imports_and_docstrings() -> None:
    """Verify all required python packages are importable with docstrings."""
    for pkg_name in REQUIRED_PACKAGES:
        module = importlib.import_module(pkg_name)
        assert module.__doc__ is not None
        assert len(module.__doc__.strip()) > 0
