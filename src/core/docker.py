"""Docker infrastructure skeleton validation and environment audit module."""

from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from core.layout import get_project_root

REQUIRED_DOCKER_SERVICES: list[str] = ["api", "qdrant", "frontend"]

REQUIRED_DOCKER_FILES: list[str] = [
    "Dockerfile",
    "docker-compose.yml",
    "frontend/Dockerfile",
]

REQUIRED_PORT_MAPPINGS: dict[str, list[str]] = {
    "api": ["8000:8000"],
    "qdrant": ["6333:6333", "6334:6334"],
    "frontend": ["5173:5173"],
}

REQUIRED_VOLUMES: list[str] = ["qdrant_data"]


def parse_docker_compose(project_root: Path | None = None) -> dict[str, Any]:
    """Parse docker-compose.yml content into structured dictionary."""
    root = project_root or get_project_root()
    compose_path = root / "docker-compose.yml"
    if not compose_path.is_file():
        return {}

    content = compose_path.read_text(encoding="utf-8")
    parsed: dict[str, Any] = yaml.safe_load(content) or {}
    return parsed


def validate_docker_setup(project_root: Path | None = None) -> dict[str, Any]:
    """Audit project repository for complete docker containerization skeleton."""
    root = project_root or get_project_root()

    missing_files: list[str] = [
        rel_path
        for rel_path in REQUIRED_DOCKER_FILES
        if not (root / rel_path).is_file()
    ]

    compose_data = parse_docker_compose(root)
    services_dict = compose_data.get("services", {}) or {}
    defined_services = list(services_dict.keys())

    missing_services: list[str] = [
        svc for svc in REQUIRED_DOCKER_SERVICES if svc not in defined_services
    ]

    volumes_dict = compose_data.get("volumes", {}) or {}
    defined_volumes = list(volumes_dict.keys())

    missing_volumes: list[str] = [
        vol for vol in REQUIRED_VOLUMES if vol not in defined_volumes
    ]

    is_valid = (
        len(missing_files) == 0
        and len(missing_services) == 0
        and len(missing_volumes) == 0
    )

    return {
        "valid": is_valid,
        "missing_files": missing_files,
        "missing_services": missing_services,
        "missing_volumes": missing_volumes,
        "services": defined_services,
        "volumes": defined_volumes,
    }
