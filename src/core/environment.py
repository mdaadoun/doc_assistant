"""Python environment and Poetry constraint validation utilities."""

import sys
from pathlib import Path
from typing import Any

MIN_PYTHON_VERSION: tuple[int, int] = (3, 11)


def get_python_version_tuple() -> tuple[int, int, int]:
    """Return runtime Python version tuple (major, minor, micro)."""
    return (
        sys.version_info[0],
        sys.version_info[1],
        sys.version_info[2],
    )


def check_python_version(min_version: tuple[int, int] = MIN_PYTHON_VERSION) -> bool:
    """Verify runtime Python version satisfies minimum version constraint."""
    return (sys.version_info[0], sys.version_info[1]) >= min_version


def locate_pyproject_toml(search_start: Path | None = None) -> Path | None:
    """Locate pyproject.toml upward from search path."""
    current = search_start or Path(__file__).resolve().parent
    for parent in [current, *current.parents]:
        candidate = parent / "pyproject.toml"
        if candidate.is_file():
            return candidate
    return None


def validate_poetry_config(pyproject_path: Path | None = None) -> dict[str, Any]:
    """Parse pyproject.toml and validate Poetry Python constraints."""
    target_path = pyproject_path or locate_pyproject_toml()
    if not target_path or not target_path.exists():
        return {"valid": False, "error": "pyproject.toml not found"}

    content = target_path.read_text(encoding="utf-8")
    has_poetry = "[tool.poetry]" in content
    has_python_constraint = "python =" in content and "^3.11" in content

    return {
        "valid": has_poetry and has_python_constraint,
        "path": str(target_path),
        "has_poetry": has_poetry,
        "has_python_constraint": has_python_constraint,
    }


def get_environment_info() -> dict[str, Any]:
    """Return dictionary summarizing runtime environment validation."""
    is_valid_python = check_python_version()
    poetry_info = validate_poetry_config()

    return {
        "python_version": f"{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}",
        "python_valid": is_valid_python,
        "poetry_valid": poetry_info.get("valid", False),
        "min_required_python": f"{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}",
        "pyproject_path": poetry_info.get("path"),
    }
