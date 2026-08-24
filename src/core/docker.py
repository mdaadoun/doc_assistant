"""Docker infrastructure skeleton validation and environment audit module."""

import re
from pathlib import Path
from typing import Any, Final

import yaml  # type: ignore[import-untyped]

from core.layout import get_project_root

REQUIRED_DOCKER_SERVICES: Final[list[str]] = ["api", "qdrant", "frontend"]

REQUIRED_DOCKER_FILES: Final[list[str]] = [
    "Dockerfile",
    "docker-compose.yml",
    "frontend/Dockerfile",
]

REQUIRED_PORT_MAPPINGS: Final[dict[str, list[str]]] = {
    "api": ["8000:8000"],
    "qdrant": ["6333:6333", "6334:6334"],
    "frontend": ["5173:5173"],
}

REQUIRED_VOLUMES: Final[list[str]] = ["qdrant_data"]

NON_ROOT_UID: Final[int] = 10001
NON_ROOT_GID: Final[int] = 10001
NON_ROOT_USER: Final[str] = "appuser"
NON_ROOT_GROUP: Final[str] = "appgroup"
REQUIRED_DOCKERFILE_STAGES: Final[list[str]] = ["builder", "runtime"]
MAX_TARGET_IMAGE_SIZE_MB: Final[int] = 250


def parse_docker_compose(project_root: Path | None = None) -> dict[str, Any]:
    """Parse docker-compose.yml content into structured dictionary."""
    root = project_root or get_project_root()
    compose_path = root / "docker-compose.yml"
    if not compose_path.is_file():
        return {}

    content = compose_path.read_text(encoding="utf-8")
    parsed: dict[str, Any] = yaml.safe_load(content) or {}
    return parsed


def parse_dockerfile_stages(
    project_root: Path | None = None, dockerfile_path: Path | str | None = None
) -> list[str]:
    """Parse multi-stage target names defined in Dockerfile."""
    root = project_root or get_project_root()
    file_path = Path(dockerfile_path) if dockerfile_path else root / "Dockerfile"
    if not file_path.is_file():
        return []

    content = file_path.read_text(encoding="utf-8")
    stage_pattern = re.compile(
        r"^FROM\s+\S+\s+AS\s+([a-zA-Z0-9_-]+)", re.IGNORECASE | re.MULTILINE
    )
    return [match.group(1).lower() for match in stage_pattern.finditer(content)]


def validate_dockerfile(
    project_root: Path | None = None, dockerfile_path: Path | str | None = None
) -> dict[str, Any]:
    """Audit Dockerfile for multi-stage structure, non-root security (UID 10001), and optimizations."""
    root = project_root or get_project_root()
    file_path = Path(dockerfile_path) if dockerfile_path else root / "Dockerfile"
    if not file_path.is_file():
        return {
            "valid": False,
            "error": f"Dockerfile not found at {file_path}",
            "stages": [],
            "missing_stages": REQUIRED_DOCKERFILE_STAGES,
            "has_multi_stage": False,
            "has_non_root_user": False,
            "has_group": False,
            "has_expose": False,
            "has_cmd": False,
            "uid": None,
            "gid": None,
        }

    content = file_path.read_text(encoding="utf-8")
    stages = parse_dockerfile_stages(root, file_path)
    missing_stages = [s for s in REQUIRED_DOCKERFILE_STAGES if s not in stages]
    has_multi_stage = len(stages) >= 2 and len(missing_stages) == 0

    has_non_root_user = str(NON_ROOT_UID) in content and (
        "USER 10001" in content
        or "USER appuser" in content
        or f"USER {NON_ROOT_USER}" in content
    )
    has_group = str(NON_ROOT_GID) in content and (
        "groupadd" in content or "appgroup" in content
    )
    has_expose = "EXPOSE 8000" in content
    has_cmd = "CMD [" in content or "ENTRYPOINT [" in content

    is_valid = (
        has_multi_stage and has_non_root_user and has_group and has_expose and has_cmd
    )

    return {
        "valid": is_valid,
        "stages": stages,
        "missing_stages": missing_stages,
        "has_multi_stage": has_multi_stage,
        "has_non_root_user": has_non_root_user,
        "has_group": has_group,
        "has_expose": has_expose,
        "has_cmd": has_cmd,
        "uid": NON_ROOT_UID if has_non_root_user else None,
        "gid": NON_ROOT_GID if has_group else None,
        "max_size_target_mb": MAX_TARGET_IMAGE_SIZE_MB,
    }


def validate_docker_setup(project_root: Path | None = None) -> dict[str, Any]:
    """Audit project repository for complete docker containerization skeleton and Dockerfile."""
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

    dockerfile_audit = validate_dockerfile(root)

    is_valid = (
        len(missing_files) == 0
        and len(missing_services) == 0
        and len(missing_volumes) == 0
        and bool(dockerfile_audit.get("valid"))
    )

    return {
        "valid": is_valid,
        "missing_files": missing_files,
        "missing_services": missing_services,
        "missing_volumes": missing_volumes,
        "services": defined_services,
        "volumes": defined_volumes,
        "dockerfile": dockerfile_audit,
    }
