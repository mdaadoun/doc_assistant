"""Unit tests for CitationDrawer React component structure, excerpts, and interactive selection."""

from pathlib import Path

from core.frontend import (
    REQUIRED_CITATION_DRAWER_IDS,
    REQUIRED_CITATION_DRAWER_PROPS,
    validate_citation_drawer_component,
)


def test_citation_drawer_component_exists_and_valid() -> None:
    """Verify CitationDrawer component satisfies all contract, prop, and inspection requirements."""
    root = Path(__file__).resolve().parent.parent.parent
    result = validate_citation_drawer_component(root)

    assert result["valid"] is True
    assert result["missing_props"] == []
    assert result["missing_ids"] == []
    assert result["has_active_inspector"] is True
    assert result["has_excerpt_copy"] is True
    assert result["has_search_filter"] is True
    assert result["has_metadata_display"] is True


def test_citation_drawer_props_interface() -> None:
    """Verify CitationDrawerProps contains essential citations, active selection and callbacks."""
    root = Path(__file__).resolve().parent.parent.parent
    comp_path = root / "frontend" / "src" / "components" / "CitationDrawer.tsx"
    content = comp_path.read_text(encoding="utf-8")

    assert "interface CitationDrawerProps" in content
    for req_prop in REQUIRED_CITATION_DRAWER_PROPS:
        assert req_prop in content
    assert "onClose" in content
    assert "title" in content


def test_citation_drawer_active_inspector_and_copy() -> None:
    """Verify active citation source excerpt inspector and copy to clipboard action."""
    root = Path(__file__).resolve().parent.parent.parent
    content = (
        root / "frontend" / "src" / "components" / "CitationDrawer.tsx"
    ).read_text(encoding="utf-8")

    assert "activeCitation" in content
    assert 'id="active-citation-inspector"' in content
    assert 'id="copy-excerpt-btn"' in content
    assert "handleCopyExcerpt" in content
    assert "navigator.clipboard.writeText" in content
    assert "active-excerpt-text" in content


def test_citation_drawer_empty_and_filter_states() -> None:
    """Verify empty citations placeholder and empty filter results rendering."""
    root = Path(__file__).resolve().parent.parent.parent
    content = (
        root / "frontend" / "src" / "components" / "CitationDrawer.tsx"
    ).read_text(encoding="utf-8")

    assert 'id="empty-citations-state"' in content
    assert 'id="empty-citations-prompt"' in content
    assert "citations.length === 0" in content
    assert "filteredCitations.length === 0" in content
    assert "No Citations Available" in content


def test_citation_drawer_search_filter_logic() -> None:
    """Verify search filter input for filtering retrieved citations by document name or excerpt."""
    root = Path(__file__).resolve().parent.parent.parent
    content = (
        root / "frontend" / "src" / "components" / "CitationDrawer.tsx"
    ).read_text(encoding="utf-8")

    assert 'id="citation-search-input"' in content
    assert "searchTerm" in content
    assert "filteredCitations" in content
    assert "c.file_name.toLowerCase()" in content
    assert "c.excerpt.toLowerCase()" in content


def test_citation_drawer_page_and_score_formatting() -> None:
    """Verify page number, relevance score formatting, and chunk ID preview."""
    root = Path(__file__).resolve().parent.parent.parent
    content = (
        root / "frontend" / "src" / "components" / "CitationDrawer.tsx"
    ).read_text(encoding="utf-8")

    assert "c.page_number" in content
    assert "c.relevance_score.toFixed(3)" in content
    assert "c.chunk_id.slice(0, 8)" in content
    assert "c.file_name" in content


def test_citation_drawer_accessibility_and_semantic_ids() -> None:
    """Verify required ARIA attributes, semantic roles, and DOM element IDs."""
    root = Path(__file__).resolve().parent.parent.parent
    content = (
        root / "frontend" / "src" / "components" / "CitationDrawer.tsx"
    ).read_text(encoding="utf-8")

    for element_id in REQUIRED_CITATION_DRAWER_IDS:
        assert f'id="{element_id}"' in content

    assert 'role="complementary"' in content
    assert 'role="list"' in content
    assert 'role="listitem"' in content
    assert "aria-label=" in content
    assert "aria-selected=" in content
    assert "tabIndex={0}" in content
    assert "handleKeyDown" in content


def test_citation_drawer_missing_file(tmp_path: Path) -> None:
    """Verify validation reports failure when CitationDrawer.tsx is missing."""
    result = validate_citation_drawer_component(tmp_path)
    assert result["valid"] is False
    assert result["missing_props"] == REQUIRED_CITATION_DRAWER_PROPS
    assert result["missing_ids"] == REQUIRED_CITATION_DRAWER_IDS
    assert result["has_active_inspector"] is False


def test_citation_drawer_incomplete_component(tmp_path: Path) -> None:
    """Verify validation detects missing elements on incomplete component."""
    comp_dir = tmp_path / "frontend" / "src" / "components"
    comp_dir.mkdir(parents=True)
    (comp_dir / "CitationDrawer.tsx").write_text(
        "export const CitationDrawer = () => <div>Incomplete</div>;\n",
        encoding="utf-8",
    )

    result = validate_citation_drawer_component(tmp_path)
    assert result["valid"] is False
    assert len(result["missing_props"]) > 0
    assert len(result["missing_ids"]) > 0
