"""Unit tests for ResponseView React component SSE streaming answer display and real-time rendering."""

from pathlib import Path

from core.frontend import (
    REQUIRED_RESPONSE_VIEW_IDS,
    REQUIRED_RESPONSE_VIEW_PROPS,
    validate_response_view_component,
)


def test_response_view_component_exists_and_valid() -> None:
    """Verify ResponseView component satisfies all contract, prop, and streaming requirements."""
    root = Path(__file__).resolve().parent.parent.parent
    result = validate_response_view_component(root)

    assert result["valid"] is True
    assert result["missing_props"] == []
    assert result["missing_ids"] == []
    assert result["has_auto_scroll"] is True
    assert result["has_streaming_cursor"] is True
    assert result["has_confidence_badge"] is True
    assert result["has_citations_display"] is True


def test_response_view_props_interface() -> None:
    """Verify ResponseViewProps contains essential message lists and streaming indicators."""
    root = Path(__file__).resolve().parent.parent.parent
    comp_path = root / "frontend" / "src" / "components" / "ResponseView.tsx"
    content = comp_path.read_text(encoding="utf-8")

    assert "interface ResponseViewProps" in content
    for req_prop in REQUIRED_RESPONSE_VIEW_PROPS:
        assert req_prop in content
    assert "onSelectCitation" in content
    assert "autoScroll" in content


def test_response_view_streaming_cursor_and_deltas() -> None:
    """Verify streaming cursor indicator is rendered conditionally during active streaming."""
    root = Path(__file__).resolve().parent.parent.parent
    content = (root / "frontend" / "src" / "components" / "ResponseView.tsx").read_text(
        encoding="utf-8"
    )

    assert "msg.isStreaming" in content
    assert 'id="streaming-cursor"' in content or "streaming-cursor" in content
    assert "▌" in content
    assert 'aria-hidden="true"' in content


def test_response_view_confidence_and_grounded_badges() -> None:
    """Verify confidence score badge calculation and grounded status indicators."""
    root = Path(__file__).resolve().parent.parent.parent
    content = (root / "frontend" / "src" / "components" / "ResponseView.tsx").read_text(
        encoding="utf-8"
    )

    assert "msg.confidenceScore" in content
    assert "0.35" in content
    assert "badge-success" in content
    assert "badge-warning" in content
    assert "msg.grounded" in content
    assert "Grounded" in content


def test_response_view_auto_scrolling_anchor() -> None:
    """Verify automatic scroll-to-bottom on stream updates using ref and scrollIntoView."""
    root = Path(__file__).resolve().parent.parent.parent
    content = (root / "frontend" / "src" / "components" / "ResponseView.tsx").read_text(
        encoding="utf-8"
    )

    assert "messagesEndRef" in content
    assert "scrollIntoView" in content
    assert "smooth" in content
    assert "useEffect" in content


def test_response_view_citations_and_finops_telemetry() -> None:
    """Verify inline citation buttons and FinOps execution metadata rendering."""
    root = Path(__file__).resolve().parent.parent.parent
    content = (root / "frontend" / "src" / "components" / "ResponseView.tsx").read_text(
        encoding="utf-8"
    )

    assert "msg.citations" in content
    assert "citation-pill" in content
    assert "onSelectCitation" in content
    assert "msg.finops" in content
    assert "total_tokens" in content
    assert "estimated_cost_usd" in content


def test_response_view_accessibility_and_semantic_ids() -> None:
    """Verify accessibility attributes, semantic roles, and DOM IDs."""
    root = Path(__file__).resolve().parent.parent.parent
    content = (root / "frontend" / "src" / "components" / "ResponseView.tsx").read_text(
        encoding="utf-8"
    )

    for element_id in REQUIRED_RESPONSE_VIEW_IDS:
        assert f'id="{element_id}"' in content

    assert 'role="log"' in content
    assert 'aria-live="polite"' in content
    assert "aria-label=" in content


def test_response_view_missing_file(tmp_path: Path) -> None:
    """Verify validation reports failure when ResponseView.tsx is missing."""
    result = validate_response_view_component(tmp_path)
    assert result["valid"] is False
    assert result["missing_props"] == REQUIRED_RESPONSE_VIEW_PROPS
    assert result["missing_ids"] == REQUIRED_RESPONSE_VIEW_IDS
    assert result["has_auto_scroll"] is False


def test_response_view_incomplete_component(tmp_path: Path) -> None:
    """Verify validation detects missing elements on incomplete component."""
    comp_dir = tmp_path / "frontend" / "src" / "components"
    comp_dir.mkdir(parents=True)
    (comp_dir / "ResponseView.tsx").write_text(
        "export const ResponseView = () => <div>Incomplete</div>;\n",
        encoding="utf-8",
    )

    result = validate_response_view_component(tmp_path)
    assert result["valid"] is False
    assert len(result["missing_props"]) > 0
    assert len(result["missing_ids"]) > 0
