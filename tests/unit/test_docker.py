"""Unit tests for Docker and docker-compose infrastructure skeleton audit."""

from pathlib import Path

from core.docker import (
    MAX_TARGET_IMAGE_SIZE_MB,
    NON_ROOT_GID,
    NON_ROOT_UID,
    REQUIRED_DOCKER_SERVICES,
    REQUIRED_DOCKERFILE_STAGES,
    REQUIRED_PORT_MAPPINGS,
    REQUIRED_VOLUMES,
    parse_docker_compose,
    parse_dockerfile_stages,
    validate_docker_setup,
    validate_dockerfile,
)


def test_docker_setup_exists_and_valid() -> None:
    """Verify docker infrastructure audit returns valid status on repository setup."""
    root = Path(__file__).resolve().parent.parent.parent
    result = validate_docker_setup(root)
    assert result["valid"] is True
    assert result["missing_files"] == []
    assert result["missing_services"] == []
    assert result["missing_volumes"] == []
    assert result["dockerfile"]["valid"] is True


def test_parse_docker_compose_structure() -> None:
    """Verify docker-compose parser extracts services, dependencies, and ports."""
    root = Path(__file__).resolve().parent.parent.parent
    parsed = parse_docker_compose(root)

    assert "services" in parsed
    services = parsed["services"]

    for svc in REQUIRED_DOCKER_SERVICES:
        assert svc in services

    assert services["api"]["depends_on"] == ["qdrant"]
    assert services["frontend"]["depends_on"] == ["api"]

    for svc, expected_ports in REQUIRED_PORT_MAPPINGS.items():
        assert services[svc]["ports"] == expected_ports

    assert "volumes" in parsed
    for vol in REQUIRED_VOLUMES:
        assert vol in parsed["volumes"]


def test_validate_docker_setup_missing_compose(tmp_path: Path) -> None:
    """Verify validation fails when docker-compose.yml is absent."""
    res = validate_docker_setup(tmp_path)
    assert res["valid"] is False
    assert "docker-compose.yml" in res["missing_files"]
    assert res["missing_services"] == REQUIRED_DOCKER_SERVICES


def test_validate_docker_setup_missing_services(tmp_path: Path) -> None:
    """Verify validation fails when docker-compose is missing required services."""
    (tmp_path / "Dockerfile").write_text(
        "FROM python:3.11-slim AS builder\nFROM python:3.11-slim AS runtime\n"
        "RUN groupadd -g 10001 appgroup && useradd -u 10001 -g appgroup appuser\n"
        'USER 10001\nEXPOSE 8000\nCMD ["uvicorn", "src.main:app"]\n',
        encoding="utf-8",
    )
    (tmp_path / "frontend").mkdir()
    (tmp_path / "frontend" / "Dockerfile").touch()
    compose_file = tmp_path / "docker-compose.yml"
    compose_file.write_text(
        "services:\n  api:\n    container_name: doc-assistant-api\n", encoding="utf-8"
    )

    res = validate_docker_setup(tmp_path)
    assert res["valid"] is False
    assert res["missing_files"] == []
    assert "qdrant" in res["missing_services"]
    assert "frontend" in res["missing_services"]


def test_validate_dockerfile_production() -> None:
    """Verify project Dockerfile meets multi-stage, non-root (UID 10001), and port constraints."""
    root = Path(__file__).resolve().parent.parent.parent
    result = validate_dockerfile(root)

    assert result["valid"] is True
    assert result["has_multi_stage"] is True
    assert result["has_non_root_user"] is True
    assert result["has_group"] is True
    assert result["has_expose"] is True
    assert result["has_cmd"] is True
    assert result["uid"] == NON_ROOT_UID == 10001
    assert result["gid"] == NON_ROOT_GID == 10001
    assert result["max_size_target_mb"] == MAX_TARGET_IMAGE_SIZE_MB == 250
    assert set(REQUIRED_DOCKERFILE_STAGES).issubset(set(result["stages"]))


def test_parse_dockerfile_stages() -> None:
    """Verify parser extracts stage target names from Dockerfile."""
    root = Path(__file__).resolve().parent.parent.parent
    stages = parse_dockerfile_stages(root)
    assert "builder" in stages
    assert "runtime" in stages


def test_validate_dockerfile_missing_file(tmp_path: Path) -> None:
    """Verify validation handles absent Dockerfile gracefully."""
    result = validate_dockerfile(tmp_path)
    assert result["valid"] is False
    assert "not found" in result["error"]
    assert result["stages"] == []


def test_validate_dockerfile_missing_non_root(tmp_path: Path) -> None:
    """Verify validation fails if Dockerfile does not enforce non-root UID 10001."""
    doc_path = tmp_path / "Dockerfile"
    doc_path.write_text(
        "FROM python:3.11-slim AS builder\n"
        "FROM python:3.11-slim AS runtime\n"
        "EXPOSE 8000\n"
        'CMD ["uvicorn", "src.main:app"]\n',
        encoding="utf-8",
    )
    result = validate_dockerfile(dockerfile_path=doc_path)
    assert result["valid"] is False
    assert result["has_multi_stage"] is True
    assert result["has_non_root_user"] is False


def test_validate_dockerfile_single_stage_fails(tmp_path: Path) -> None:
    """Verify validation fails if Dockerfile is not multi-stage."""
    doc_path = tmp_path / "Dockerfile"
    doc_path.write_text(
        "FROM python:3.11-slim\n"
        "RUN groupadd -g 10001 appgroup && useradd -u 10001 -g appgroup appuser\n"
        "USER 10001\n"
        "EXPOSE 8000\n"
        'CMD ["uvicorn", "src.main:app"]\n',
        encoding="utf-8",
    )
    result = validate_dockerfile(dockerfile_path=doc_path)
    assert result["valid"] is False
    assert result["has_multi_stage"] is False
