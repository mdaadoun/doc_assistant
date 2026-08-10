"""Unit tests for Docker and docker-compose infrastructure skeleton audit."""

from pathlib import Path

from core.docker import (
    REQUIRED_DOCKER_SERVICES,
    REQUIRED_PORT_MAPPINGS,
    REQUIRED_VOLUMES,
    parse_docker_compose,
    validate_docker_setup,
)


def test_docker_setup_exists_and_valid() -> None:
    """Verify docker infrastructure audit returns valid status on repository setup."""
    root = Path(__file__).resolve().parent.parent.parent
    result = validate_docker_setup(root)
    assert result["valid"] is True
    assert result["missing_files"] == []
    assert result["missing_services"] == []
    assert result["missing_volumes"] == []


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
    (tmp_path / "Dockerfile").touch()
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
