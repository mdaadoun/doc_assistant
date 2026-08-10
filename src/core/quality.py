"""Validation logic for Ruff, Mypy, and pre-commit detect-secrets configs."""

import json
from pathlib import Path
from typing import Any

from core.environment import locate_pyproject_toml


def validate_ruff_config(base_dir: Path | None = None) -> dict[str, Any]:
    """Validate presence and basic fields of ruff.toml."""
    root = base_dir or Path(__file__).resolve().parent.parent.parent
    ruff_path = root / "ruff.toml"
    if not ruff_path.is_file():
        return {"valid": False, "error": "ruff.toml missing"}

    content = ruff_path.read_text(encoding="utf-8")
    has_select = "select =" in content
    has_isort = "[lint.isort]" in content
    has_target = 'target-version = "py311"' in content

    return {
        "valid": has_select and has_isort and has_target,
        "path": str(ruff_path),
        "has_select": has_select,
        "has_isort": has_isort,
        "has_target": has_target,
    }


def validate_pre_commit_config(base_dir: Path | None = None) -> dict[str, Any]:
    """Validate presence and required hooks in .pre-commit-config.yaml."""
    root = base_dir or Path(__file__).resolve().parent.parent.parent
    pc_path = root / ".pre-commit-config.yaml"
    if not pc_path.is_file():
        return {"valid": False, "error": ".pre-commit-config.yaml missing"}

    content = pc_path.read_text(encoding="utf-8")
    has_ruff = "ruff" in content
    has_mypy = "mypy" in content
    has_secrets = "detect-secrets" in content

    return {
        "valid": has_ruff and has_mypy and has_secrets,
        "path": str(pc_path),
        "has_ruff": has_ruff,
        "has_mypy": has_mypy,
        "has_secrets": has_secrets,
    }


def validate_detect_secrets_baseline(base_dir: Path | None = None) -> dict[str, Any]:
    """Validate presence and structural integrity of .secrets.baseline."""
    root = base_dir or Path(__file__).resolve().parent.parent.parent
    baseline_path = root / ".secrets.baseline"
    if not baseline_path.is_file():
        return {"valid": False, "error": ".secrets.baseline missing"}

    try:
        data = json.loads(baseline_path.read_text(encoding="utf-8"))
        has_version = "version" in data
        has_plugins = "plugins_used" in data
        has_results = "results" in data
        valid = has_version and has_plugins and has_results
        return {
            "valid": valid,
            "path": str(baseline_path),
            "version": data.get("version"),
        }
    except json.JSONDecodeError as exc:
        return {"valid": False, "error": f"Invalid JSON: {exc}"}


def validate_quality_configs(base_dir: Path | None = None) -> dict[str, Any]:
    """Audit all static code quality tool configuration files."""
    root = base_dir or Path(__file__).resolve().parent.parent.parent
    pyproject = locate_pyproject_toml(root)

    ruff_res = validate_ruff_config(root)
    pc_res = validate_pre_commit_config(root)
    ds_res = validate_detect_secrets_baseline(root)

    all_valid = (
        bool(pyproject and pyproject.exists())
        and ruff_res.get("valid", False)
        and pc_res.get("valid", False)
        and ds_res.get("valid", False)
    )

    return {
        "valid": all_valid,
        "ruff": ruff_res,
        "pre_commit": pc_res,
        "detect_secrets": ds_res,
    }
