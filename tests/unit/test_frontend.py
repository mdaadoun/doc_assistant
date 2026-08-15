"""Unit tests for React 18+ / Vite / TypeScript frontend project structure."""

from pathlib import Path

from core.frontend import (
    REQUIRED_DEPENDENCIES,
    REQUIRED_DEV_DEPENDENCIES,
    REQUIRED_PACKAGE_SCRIPTS,
    REQUIRED_TS_INTERFACES,
    parse_frontend_package_json,
    parse_frontend_tsconfig,
    validate_frontend_setup,
)
from models.chat import ChatRequest, ChatResponse, Citation, FinOpsMetadata


def test_frontend_setup_exists_and_valid() -> None:
    """Verify frontend project passes all structural, configuration, and interface audits."""
    root = Path(__file__).resolve().parent.parent.parent
    result = validate_frontend_setup(root)
    assert result["valid"] is True
    assert result["missing_files"] == []
    assert result["missing_scripts"] == []
    assert result["missing_dependencies"] == []
    assert result["missing_dev_dependencies"] == []
    assert result["missing_interfaces"] == []


def test_parse_frontend_package_json() -> None:
    """Verify package.json contains required scripts and core dependencies."""
    root = Path(__file__).resolve().parent.parent.parent
    pkg_data = parse_frontend_package_json(root)

    assert pkg_data.get("name") == "doc-assistant-frontend"
    assert pkg_data.get("type") == "module"

    scripts = pkg_data.get("scripts", {})
    for req_script in REQUIRED_PACKAGE_SCRIPTS:
        assert req_script in scripts

    deps = pkg_data.get("dependencies", {})
    for req_dep in REQUIRED_DEPENDENCIES:
        assert req_dep in deps

    dev_deps = pkg_data.get("devDependencies", {})
    for req_dev in REQUIRED_DEV_DEPENDENCIES:
        assert req_dev in dev_deps


def test_parse_frontend_tsconfig() -> None:
    """Verify tsconfig.json is configured with strict mode and JSX support."""
    root = Path(__file__).resolve().parent.parent.parent
    tsconfig = parse_frontend_tsconfig(root)

    compiler_opts = tsconfig.get("compilerOptions", {})
    assert compiler_opts.get("strict") is True
    assert compiler_opts.get("jsx") == "react-jsx"
    assert compiler_opts.get("moduleResolution") == "bundler"


def test_validate_frontend_setup_missing_package(tmp_path: Path) -> None:
    """Verify validation reports missing files and dependencies for empty directory."""
    result = validate_frontend_setup(tmp_path)
    assert result["valid"] is False
    assert "package.json" in result["missing_files"]
    assert result["missing_dependencies"] == REQUIRED_DEPENDENCIES
    assert result["missing_dev_dependencies"] == REQUIRED_DEV_DEPENDENCIES
    assert result["missing_interfaces"] == REQUIRED_TS_INTERFACES


def test_validate_frontend_setup_missing_interfaces(tmp_path: Path) -> None:
    """Verify validation detects missing TypeScript interface declarations."""
    frontend_dir = tmp_path / "frontend"
    types_dir = frontend_dir / "src" / "types"
    types_dir.mkdir(parents=True)
    (types_dir / "index.ts").write_text("export interface Dummy {}\n", encoding="utf-8")
    (frontend_dir / "package.json").write_text("{}", encoding="utf-8")

    result = validate_frontend_setup(tmp_path)
    assert result["valid"] is False
    assert "Citation" in result["missing_interfaces"]
    assert "ChatResponse" in result["missing_interfaces"]


def test_typescript_contracts_parity_with_python_models() -> None:
    """Verify key domain model fields in Python exist in TypeScript definitions."""
    root = Path(__file__).resolve().parent.parent.parent
    types_content = (root / "frontend" / "src" / "types" / "index.ts").read_text(
        encoding="utf-8"
    )

    for model_cls in (ChatRequest, ChatResponse, Citation, FinOpsMetadata):
        for field_name in model_cls.model_fields:
            assert (
                field_name in types_content
            ), f"Field '{field_name}' from {model_cls.__name__} missing in TS types."
