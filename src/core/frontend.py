"""Frontend project structure and TypeScript configuration audit module."""

import json
from pathlib import Path
from typing import Any, Final

from core.layout import get_project_root

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
]

REQUIRED_QUERY_INPUT_PROPS: Final[list[str]] = [
    "onSubmit",
    "isLoading",
]

REQUIRED_QUERY_INPUT_IDS: Final[list[str]] = [
    "query-form",
    "query-input",
    "top-k-select",
    "submit-query-btn",
]

REQUIRED_RESPONSE_VIEW_PROPS: Final[list[str]] = [
    "messages",
    "isStreaming",
]

REQUIRED_RESPONSE_VIEW_IDS: Final[list[str]] = [
    "response-view",
    "streaming-cursor",
    "empty-state-prompt",
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


def validate_query_input_component(
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Audit QueryInput React component for contract compliance, submission handling and a11y."""
    root = project_root or get_project_root()
    comp_file = root / "frontend" / "src" / "components" / "QueryInput.tsx"
    if not comp_file.is_file():
        return {
            "valid": False,
            "error": "QueryInput.tsx file not found",
            "missing_props": REQUIRED_QUERY_INPUT_PROPS,
            "missing_ids": REQUIRED_QUERY_INPUT_IDS,
            "has_submission_guard": False,
            "has_keyboard_shortcut": False,
            "has_top_k_selector": False,
        }

    content = comp_file.read_text(encoding="utf-8")
    missing_props = [p for p in REQUIRED_QUERY_INPUT_PROPS if p not in content]
    missing_ids = [i for i in REQUIRED_QUERY_INPUT_IDS if i not in content]
    has_sub_guard = "trim()" in content and "onSubmit(" in content
    has_kb_shortcut = "Enter" in content and "shiftKey" in content
    has_top_k = "top_k" in content or "topK" in content or "top-k" in content

    is_valid = (
        len(missing_props) == 0
        and len(missing_ids) == 0
        and has_sub_guard
        and has_kb_shortcut
        and has_top_k
    )
    return {
        "valid": is_valid,
        "missing_props": missing_props,
        "missing_ids": missing_ids,
        "has_submission_guard": has_sub_guard,
        "has_keyboard_shortcut": has_kb_shortcut,
        "has_top_k_selector": has_top_k,
    }


def validate_response_view_component(
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Audit ResponseView React component for SSE streaming real-time rendering compliance."""
    root = project_root or get_project_root()
    comp_file = root / "frontend" / "src" / "components" / "ResponseView.tsx"
    if not comp_file.is_file():
        return {
            "valid": False,
            "error": "ResponseView.tsx file not found",
            "missing_props": REQUIRED_RESPONSE_VIEW_PROPS,
            "missing_ids": REQUIRED_RESPONSE_VIEW_IDS,
            "has_auto_scroll": False,
            "has_streaming_cursor": False,
            "has_confidence_badge": False,
            "has_citations_display": False,
        }

    content = comp_file.read_text(encoding="utf-8")
    missing_props = [p for p in REQUIRED_RESPONSE_VIEW_PROPS if p not in content]
    missing_ids = [i for i in REQUIRED_RESPONSE_VIEW_IDS if i not in content]
    has_auto_scroll = "scrollIntoView" in content or "useRef" in content
    has_streaming_cursor = "streaming-cursor" in content or "isStreaming" in content
    has_confidence_badge = "confidenceScore" in content or "0.35" in content
    has_citations_display = "citations" in content and "citation-pill" in content

    is_valid = (
        len(missing_props) == 0
        and len(missing_ids) == 0
        and has_auto_scroll
        and has_streaming_cursor
        and has_confidence_badge
        and has_citations_display
    )
    return {
        "valid": is_valid,
        "missing_props": missing_props,
        "missing_ids": missing_ids,
        "has_auto_scroll": has_auto_scroll,
        "has_streaming_cursor": has_streaming_cursor,
        "has_confidence_badge": has_confidence_badge,
        "has_citations_display": has_citations_display,
    }
