"""Unit tests for Ruff, Mypy strict, pre-commit, and detect-secrets baseline."""

from pathlib import Path

from core.quality import (
    validate_detect_secrets_baseline,
    validate_pre_commit_config,
    validate_quality_configs,
    validate_ruff_config,
)


def test_ruff_toml_exists_and_configured() -> None:
    """Verify ruff.toml exists and configures lint rules and py311 target."""
    root = Path(__file__).resolve().parent.parent.parent
    ruff_path = root / "ruff.toml"
    assert ruff_path.is_file()

    res = validate_ruff_config(root)
    assert res["valid"] is True
    assert res["has_select"] is True
    assert res["has_isort"] is True
    assert res["has_target"] is True


def test_pre_commit_config_exists_and_valid() -> None:
    """Verify .pre-commit-config.yaml exists and defines ruff, mypy, and secrets hooks."""
    root = Path(__file__).resolve().parent.parent.parent
    res = validate_pre_commit_config(root)
    assert res["valid"] is True
    assert res["has_ruff"] is True
    assert res["has_mypy"] is True
    assert res["has_secrets"] is True


def test_detect_secrets_baseline_exists_and_valid() -> None:
    """Verify .secrets.baseline exists and has valid json schema."""
    root = Path(__file__).resolve().parent.parent.parent
    baseline_path = root / ".secrets.baseline"
    assert baseline_path.is_file()

    res = validate_detect_secrets_baseline(root)
    assert res["valid"] is True
    assert "version" in res


def test_overall_quality_configs_audit() -> None:
    """Verify validate_quality_configs returns true across all tooling."""
    root = Path(__file__).resolve().parent.parent.parent
    res = validate_quality_configs(root)
    assert res["valid"] is True
    assert res["ruff"]["valid"] is True
    assert res["pre_commit"]["valid"] is True
    assert res["detect_secrets"]["valid"] is True


def test_invalid_secrets_baseline_handling(tmp_path: Path) -> None:
    """Verify error handling on malformed JSON baseline file."""
    bad_file = tmp_path / ".secrets.baseline"
    bad_file.write_text("invalid json content", encoding="utf-8")
    res = validate_detect_secrets_baseline(tmp_path)
    assert res["valid"] is False
    assert "error" in res
