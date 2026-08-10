"""Unit tests for Poetry pyproject.toml configuration and constraints."""

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]

from pathlib import Path


def test_pyproject_file_exists() -> None:
    """Verify pyproject.toml exists in the project root."""
    root_dir = Path(__file__).resolve().parent.parent.parent
    pyproject_path = root_dir / "pyproject.toml"
    assert pyproject_path.is_file()


def test_pyproject_poetry_metadata() -> None:
    """Verify Poetry metadata, Python constraints, and package definitions."""
    root_dir = Path(__file__).resolve().parent.parent.parent
    pyproject_path = root_dir / "pyproject.toml"

    with pyproject_path.open("rb") as f:
        data = tomllib.load(f)

    assert "tool" in data
    assert "poetry" in data["tool"]

    poetry_cfg = data["tool"]["poetry"]
    assert poetry_cfg["name"] == "doc-assistant"
    assert poetry_cfg["dependencies"]["python"] == "^3.11"

    packages = poetry_cfg.get("packages", [])
    package_includes = [pkg["include"] for pkg in packages]
    assert "core" in package_includes
    assert "api" in package_includes


def test_pyproject_tool_configurations() -> None:
    """Verify Ruff, Mypy, and Pytest configs match Python 3.11+ target."""
    root_dir = Path(__file__).resolve().parent.parent.parent
    pyproject_path = root_dir / "pyproject.toml"

    with pyproject_path.open("rb") as f:
        data = tomllib.load(f)

    tool_cfg = data.get("tool", {})

    assert tool_cfg.get("ruff", {}).get("target-version") == "py311"
    assert tool_cfg.get("mypy", {}).get("python_version") == "3.11"
    assert tool_cfg.get("mypy", {}).get("strict") is True
