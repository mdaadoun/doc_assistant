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

    missing_files: list[str] = [
        rel_path
        for rel_path in REQUIRED_FRONTEND_FILES
        if not (frontend_dir / rel_path).is_file()
    ]

    pkg_data = parse_frontend_package_json(root)
    scripts = pkg_data.get("scripts", {}) or {}
    missing_scripts = [s for s in REQUIRED_PACKAGE_SCRIPTS if s not in scripts]

    deps = pkg_data.get("dependencies", {}) or {}
    missing_deps = [d for d in REQUIRED_DEPENDENCIES if d not in deps]

    dev_deps = pkg_data.get("devDependencies", {}) or {}
    missing_dev_deps = [d for d in REQUIRED_DEV_DEPENDENCIES if d not in dev_deps]

    # Validate TypeScript interfaces presence in types/index.ts
    types_file = frontend_dir / "src" / "types" / "index.ts"
    missing_interfaces: list[str] = []
    if types_file.is_file():
        content = types_file.read_text(encoding="utf-8")
        for iface in REQUIRED_TS_INTERFACES:
            if f"interface {iface}" not in content:
                missing_interfaces.append(iface)
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
