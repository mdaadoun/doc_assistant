"""Frontend project structure and TypeScript configuration audit module."""

import json
from pathlib import Path
from typing import Any, Final

from core.frontend_validators import (
    REQUIRED_CITATION_DRAWER_IDS,
    REQUIRED_CITATION_DRAWER_PROPS,
    REQUIRED_QUERY_INPUT_IDS,
    REQUIRED_QUERY_INPUT_PROPS,
    REQUIRED_RESPONSE_VIEW_IDS,
    REQUIRED_RESPONSE_VIEW_PROPS,
    validate_citation_drawer_component,
    validate_query_input_component,
    validate_response_view_component,
)
from core.layout import get_project_root
from core.resilience_validators import (
    REQUIRED_CONFIDENCE_INDICATOR_IDS,
    REQUIRED_CONFIDENCE_INDICATOR_PROPS,
    REQUIRED_ERROR_BANNER_IDS,
    REQUIRED_ERROR_BANNER_PROPS,
    REQUIRED_LOADING_INDICATOR_IDS,
    REQUIRED_LOADING_INDICATOR_PROPS,
    validate_confidence_indicator_component,
    validate_error_banner_component,
    validate_loading_indicator_component,
    validate_resilience_and_confidence_components,
)

REQUIRED_FRONTEND_FILES: Final[list[str]] = [
    "package.json",
    "tsconfig.json",
    "tsconfig.node.json",
    "vite.config.ts",
    "index.html",
    "src/main.tsx",
    "src/App.tsx",
    "src/index.css",
    "src/types/index.ts",
    "src/services/api.ts",
    "src/components/Header.tsx",
    "src/components/QueryInput.tsx",
    "src/components/CitationDrawer.tsx",
    "src/components/ResponseView.tsx",
    "src/components/ConfidenceIndicator.tsx",
    "src/components/ErrorBanner.tsx",
    "src/components/LoadingIndicator.tsx",
]

REQUIRED_PACKAGE_SCRIPTS: Final[list[str]] = [
    "dev",
    "build",
    "preview",
    "typecheck",
]

REQUIRED_DEPENDENCIES: Final[list[str]] = [
    "react",
    "react-dom",
]

REQUIRED_DEV_DEPENDENCIES: Final[list[str]] = [
    "@vitejs/plugin-react",
    "typescript",
    "vite",
]

REQUIRED_TS_INTERFACES: Final[list[str]] = [
    "Citation",
    "FinOpsMetadata",
    "ChatRequest",
    "ChatResponse",
    "RetrievalResult",
    "DebugRetrievalResponse",
    "SSEMetaDataPayload",
    "SSETokenPayload",
    "SSEDonePayload",
    "SSEErrorPayload",
    "ErrorInfo",
]


def parse_frontend_package_json(
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Parse frontend package.json content into structured dictionary."""
    root = project_root or get_project_root()
    pkg_path = root / "frontend" / "package.json"
    if not pkg_path.is_file():
        return {}
    try:
        data: dict[str, Any] = json.loads(pkg_path.read_text(encoding="utf-8"))
        return data
    except json.JSONDecodeError:
        return {}


def parse_frontend_tsconfig(
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Parse frontend tsconfig.json content into structured dictionary."""
    root = project_root or get_project_root()
    ts_path = root / "frontend" / "tsconfig.json"
    if not ts_path.is_file():
        return {}
    try:
        data: dict[str, Any] = json.loads(ts_path.read_text(encoding="utf-8"))
        return data
    except json.JSONDecodeError:
        return {}


def validate_frontend_setup(
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Audit project repository for complete React 18+ / Vite / TypeScript frontend."""
    root = project_root or get_project_root()
    frontend_dir = root / "frontend"

    missing_files = [
        p for p in REQUIRED_FRONTEND_FILES if not (frontend_dir / p).is_file()
    ]
    pkg_data = parse_frontend_package_json(root)
    scripts = pkg_data.get("scripts", {}) or {}
    missing_scripts = [s for s in REQUIRED_PACKAGE_SCRIPTS if s not in scripts]
    deps = pkg_data.get("dependencies", {}) or {}
    missing_deps = [d for d in REQUIRED_DEPENDENCIES if d not in deps]
    dev_deps = pkg_data.get("devDependencies", {}) or {}
    missing_dev_deps = [d for d in REQUIRED_DEV_DEPENDENCIES if d not in dev_deps]

    types_file = frontend_dir / "src" / "types" / "index.ts"
    missing_interfaces: list[str] = []
    if types_file.is_file():
        content = types_file.read_text(encoding="utf-8")
        missing_interfaces = [
            i for i in REQUIRED_TS_INTERFACES if f"interface {i}" not in content
        ]
    else:
        missing_interfaces = list(REQUIRED_TS_INTERFACES)

    is_valid = (
        len(missing_files) == 0
        and len(missing_scripts) == 0
        and len(missing_deps) == 0
        and len(missing_dev_deps) == 0
        and len(missing_interfaces) == 0
    )
    return {
        "valid": is_valid,
        "missing_files": missing_files,
        "missing_scripts": missing_scripts,
        "missing_dependencies": missing_deps,
        "missing_dev_dependencies": missing_dev_deps,
        "missing_interfaces": missing_interfaces,
    }


__all__ = [
    "REQUIRED_CITATION_DRAWER_IDS",
    "REQUIRED_CITATION_DRAWER_PROPS",
    "REQUIRED_CONFIDENCE_INDICATOR_IDS",
    "REQUIRED_CONFIDENCE_INDICATOR_PROPS",
    "REQUIRED_DEPENDENCIES",
    "REQUIRED_DEV_DEPENDENCIES",
    "REQUIRED_ERROR_BANNER_IDS",
    "REQUIRED_ERROR_BANNER_PROPS",
    "REQUIRED_FRONTEND_FILES",
    "REQUIRED_LOADING_INDICATOR_IDS",
    "REQUIRED_LOADING_INDICATOR_PROPS",
    "REQUIRED_PACKAGE_SCRIPTS",
    "REQUIRED_QUERY_INPUT_IDS",
    "REQUIRED_QUERY_INPUT_PROPS",
    "REQUIRED_RESPONSE_VIEW_IDS",
    "REQUIRED_RESPONSE_VIEW_PROPS",
    "REQUIRED_TS_INTERFACES",
    "parse_frontend_package_json",
    "parse_frontend_tsconfig",
    "validate_citation_drawer_component",
    "validate_confidence_indicator_component",
    "validate_error_banner_component",
    "validate_frontend_setup",
    "validate_loading_indicator_component",
    "validate_query_input_component",
    "validate_resilience_and_confidence_components",
    "validate_response_view_component",
]
