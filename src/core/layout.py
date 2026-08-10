"""Package layout validation and module registry for Doc Assistant."""

from pathlib import Path
from typing import Any, Final

REQUIRED_PACKAGES: Final[tuple[str, ...]] = (
    "api",
    "retrieval",
    "generation",
    "ingestion",
    "clients",
    "models",
    "core",
    "cache",
)

REQUIRED_DIRECTORIES: Final[tuple[str, ...]] = (
    "src",
    "frontend",
    "tests",
)


def get_project_root() -> Path:
    """Return absolute Path to project root directory."""
    return Path(__file__).resolve().parent.parent.parent


def validate_package_layout(base_dir: Path | None = None) -> dict[str, Any]:
    """Validate modular package layout and directory structure presence."""
    root = base_dir or get_project_root()
    src_dir = root / "src"

    package_status: dict[str, bool] = {}
    missing_packages: list[str] = []

    for pkg in REQUIRED_PACKAGES:
        pkg_path = src_dir / pkg
        init_file = pkg_path / "__init__.py"
        is_valid = pkg_path.is_dir() and init_file.is_file()
        package_status[pkg] = is_valid
        if not is_valid:
            missing_packages.append(pkg)

    directories_status: dict[str, bool] = {}
    missing_directories: list[str] = []

    for d in REQUIRED_DIRECTORIES:
        d_path = root / d
        is_valid = d_path.is_dir()
        directories_status[d] = is_valid
        if not is_valid:
            missing_directories.append(d)

    is_complete = len(missing_packages) == 0 and len(missing_directories) == 0

    return {
        "status": "VALID" if is_complete else "INVALID",
        "is_complete": is_complete,
        "packages": package_status,
        "directories": directories_status,
        "missing_packages": missing_packages,
        "missing_directories": missing_directories,
        "root_path": str(root),
    }
