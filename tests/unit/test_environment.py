"""Unit tests for Python environment and version constraint validation."""

from unittest.mock import patch

from core.environment import (
    MIN_PYTHON_VERSION,
    check_python_version,
    get_environment_info,
    get_python_version_tuple,
    locate_pyproject_toml,
    validate_poetry_config,
)


def test_get_python_version_tuple() -> None:
    """Verify get_python_version_tuple returns 3-element integer tuple."""
    ver = get_python_version_tuple()
    assert len(ver) == 3
    assert all(isinstance(x, int) for x in ver)


def test_check_python_version_real() -> None:
    """Verify runtime Python version is at least 3.11 in test environment."""
    assert check_python_version(MIN_PYTHON_VERSION) is True


def test_check_python_version_mocked() -> None:
    """Verify check_python_version logic with simulated version tuples."""
    with patch("sys.version_info", (3, 11, 0, "final", 0)):
        assert check_python_version((3, 11)) is True

    with patch("sys.version_info", (3, 10, 12, "final", 0)):
        assert check_python_version((3, 11)) is False


def test_locate_pyproject_toml() -> None:
    """Verify locate_pyproject_toml finds existing pyproject.toml."""
    path = locate_pyproject_toml()
    assert path is not None
    assert path.name == "pyproject.toml"
    assert path.exists()


def test_validate_poetry_config() -> None:
    """Verify validate_poetry_config parses pyproject.toml correctly."""
    result = validate_poetry_config()
    assert result["valid"] is True
    assert result["has_poetry"] is True
    assert result["has_python_constraint"] is True


def test_get_environment_info() -> None:
    """Verify get_environment_info returns complete summary metadata."""
    info = get_environment_info()
    assert "python_version" in info
    assert info["python_valid"] is True
    assert info["poetry_valid"] is True
    assert info["min_required_python"] == "3.11"
