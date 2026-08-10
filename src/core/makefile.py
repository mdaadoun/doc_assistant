"""Makefile structure validation and developer shortcut configuration audit."""

import re
from pathlib import Path
from typing import Any

from core.layout import get_project_root

REQUIRED_MAKEFILE_TARGETS: list[str] = [
    "help",
    "install",
    "clean",
    "lint",
    "format",
    "typecheck",
    "test",
    "dev",
    "run",
    "docker-build",
    "docker-run",
]


def parse_makefile_targets(project_root: Path | None = None) -> list[str]:
    """Parse target names defined in project Makefile."""
    root = project_root or get_project_root()
    makefile = root / "Makefile"
    if not makefile.is_file():
        return []

    content = makefile.read_text(encoding="utf-8")
    targets: list[str] = []
    target_pattern = re.compile(r"^([a-zA-Z0-9_-]+):", re.MULTILINE)
    for match in target_pattern.finditer(content):
        target = match.group(1)
        if target not in targets:
            targets.append(target)
    return targets


def validate_makefile(project_root: Path | None = None) -> dict[str, Any]:
    """Audit project Makefile for mandatory developer shortcut targets and .PHONY."""
    root = project_root or get_project_root()
    makefile = root / "Makefile"
    if not makefile.is_file():
        return {
            "valid": False,
            "error": "Makefile not found",
            "targets": [],
            "missing_targets": REQUIRED_MAKEFILE_TARGETS,
            "has_phony": False,
        }

    content = makefile.read_text(encoding="utf-8")
    targets = parse_makefile_targets(root)
    missing = [t for t in REQUIRED_MAKEFILE_TARGETS if t not in targets]
    has_phony = ".PHONY:" in content

    is_valid = len(missing) == 0 and has_phony

    return {
        "valid": is_valid,
        "targets": targets,
        "missing_targets": missing,
        "has_phony": has_phony,
    }
