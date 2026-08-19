"""Frontend React component contract and accessibility validation module."""

from pathlib import Path
from typing import Any, Final

from core.layout import get_project_root

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

REQUIRED_CITATION_DRAWER_PROPS: Final[list[str]] = [
    "citations",
    "activeCitation",
    "onSelectCitation",
]

REQUIRED_CITATION_DRAWER_IDS: Final[list[str]] = [
    "citation-drawer",
    "citations-count-badge",
    "empty-citations-state",
    "citations-list",
]


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


def validate_citation_drawer_component(
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Audit CitationDrawer React component for citation excerpts, selection and accessibility."""
    root = project_root or get_project_root()
    comp_file = root / "frontend" / "src" / "components" / "CitationDrawer.tsx"
    if not comp_file.is_file():
        return {
            "valid": False,
            "error": "CitationDrawer.tsx file not found",
            "missing_props": REQUIRED_CITATION_DRAWER_PROPS,
            "missing_ids": REQUIRED_CITATION_DRAWER_IDS,
            "has_active_inspector": False,
            "has_excerpt_copy": False,
            "has_search_filter": False,
            "has_metadata_display": False,
        }

    content = comp_file.read_text(encoding="utf-8")
    missing_props = [p for p in REQUIRED_CITATION_DRAWER_PROPS if p not in content]
    missing_ids = [i for i in REQUIRED_CITATION_DRAWER_IDS if i not in content]
    has_inspector = "activeCitation" in content and (
        "inspector" in content or "active-citation" in content
    )
    has_copy = (
        "clipboard" in content or "handleCopyExcerpt" in content or "Copy" in content
    )
    has_filter = "filter" in content or "searchTerm" in content or "search" in content
    has_meta = (
        "page_number" in content
        and "relevance_score" in content
        and "file_name" in content
    )

    is_valid = (
        len(missing_props) == 0
        and len(missing_ids) == 0
        and has_inspector
        and has_copy
        and has_filter
        and has_meta
    )
    return {
        "valid": is_valid,
        "missing_props": missing_props,
        "missing_ids": missing_ids,
        "has_active_inspector": has_inspector,
        "has_excerpt_copy": has_copy,
        "has_search_filter": has_filter,
        "has_metadata_display": has_meta,
    }
