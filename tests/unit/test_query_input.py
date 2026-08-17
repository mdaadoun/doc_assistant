"""Unit tests for QueryInput React component structure, props, and submission handling."""

from pathlib import Path

from core.frontend import (
    REQUIRED_QUERY_INPUT_IDS,
    REQUIRED_QUERY_INPUT_PROPS,
    validate_query_input_component,
)


def test_query_input_component_exists_and_valid() -> None:
    """Verify QueryInput component satisfies all contract, prop, and a11y requirements."""
    root = Path(__file__).resolve().parent.parent.parent
    result = validate_query_input_component(root)

    assert result["valid"] is True
    assert result["missing_props"] == []
    assert result["missing_ids"] == []
    assert result["has_submission_guard"] is True
    assert result["has_keyboard_shortcut"] is True
    assert result["has_top_k_selector"] is True


def test_query_input_props_interface() -> None:
    """Verify QueryInputProps contains essential handlers and configuration options."""
    root = Path(__file__).resolve().parent.parent.parent
    component_path = root / "frontend" / "src" / "components" / "QueryInput.tsx"
    content = component_path.read_text(encoding="utf-8")

    assert "interface QueryInputProps" in content
    for req_prop in REQUIRED_QUERY_INPUT_PROPS:
        assert req_prop in content
    assert "suggestedQueries" in content
    assert "placeholder" in content
    assert "maxQueryLength" in content


def test_query_input_keyboard_shortcuts() -> None:
    """Verify Enter submits and Shift+Enter enables multiline query input."""
    root = Path(__file__).resolve().parent.parent.parent
    content = (root / "frontend" / "src" / "components" / "QueryInput.tsx").read_text(
        encoding="utf-8"
    )

    assert "handleKeyDown" in content
    assert "Enter" in content
    assert "!e.shiftKey" in content
    assert "e.preventDefault()" in content


def test_query_input_submission_guards_and_trim() -> None:
    """Verify whitespace trimming and prevention of empty query submission."""
    root = Path(__file__).resolve().parent.parent.parent
    content = (root / "frontend" / "src" / "components" / "QueryInput.tsx").read_text(
        encoding="utf-8"
    )

    assert "query.trim()" in content
    assert "onSubmit(trimmed, topK)" in content or "onSubmit(" in content
    assert "isInteractiveDisabled" in content or "disabled" in content


def test_query_input_accessibility_and_semantic_ids() -> None:
    """Verify required ARIA attributes, semantic roles, and DOM IDs."""
    root = Path(__file__).resolve().parent.parent.parent
    content = (root / "frontend" / "src" / "components" / "QueryInput.tsx").read_text(
        encoding="utf-8"
    )

    for element_id in REQUIRED_QUERY_INPUT_IDS:
        assert f'id="{element_id}"' in content

    assert 'role="form"' in content
    assert "aria-label=" in content
    assert "aria-busy=" in content


def test_query_input_top_k_options() -> None:
    """Verify context chunk (top_k) selector options are configured."""
    root = Path(__file__).resolve().parent.parent.parent
    content = (root / "frontend" / "src" / "components" / "QueryInput.tsx").read_text(
        encoding="utf-8"
    )

    assert "<select" in content
    assert "topK" in content
    assert "value={3}" in content or "value={5}" in content


def test_query_input_missing_file(tmp_path: Path) -> None:
    """Verify validation reports failure when QueryInput.tsx is missing."""
    result = validate_query_input_component(tmp_path)
    assert result["valid"] is False
    assert result["missing_props"] == REQUIRED_QUERY_INPUT_PROPS
    assert result["missing_ids"] == REQUIRED_QUERY_INPUT_IDS
    assert result["has_submission_guard"] is False


def test_query_input_incomplete_component(tmp_path: Path) -> None:
    """Verify validation detects missing props on incomplete component."""
    component_dir = tmp_path / "frontend" / "src" / "components"
    component_dir.mkdir(parents=True)
    (component_dir / "QueryInput.tsx").write_text(
        "export const QueryInput = () => <div>Incomplete</div>;\n",
        encoding="utf-8",
    )

    result = validate_query_input_component(tmp_path)
    assert result["valid"] is False
    assert len(result["missing_props"]) > 0
    assert len(result["missing_ids"]) > 0
