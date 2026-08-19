import React, { useState, useMemo } from "react";
import { Citation } from "../types";

export interface CitationDrawerProps {
  citations: Citation[];
  activeCitation: Citation | null;
  onSelectCitation: (citation: Citation | null) => void;
  onClose?: () => void;
  title?: string;
}

export const CitationDrawer: React.FC<CitationDrawerProps> = ({
  citations,
  activeCitation,
  onSelectCitation,
  onClose,
  title = "Grounded Citations",
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [copiedChunkId, setCopiedChunkId] = useState<string | null>(null);

  const filteredCitations = useMemo(() => {
    if (!searchTerm.trim()) return citations;
    const term = searchTerm.toLowerCase();
    return citations.filter(
      (c) =>
        c.file_name.toLowerCase().includes(term) ||
        c.excerpt.toLowerCase().includes(term) ||
        c.chunk_id.toLowerCase().includes(term)
    );
  }, [citations, searchTerm]);

  const handleCopyExcerpt = async (citation: Citation, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(citation.excerpt);
      }
    } finally {
      setCopiedChunkId(citation.chunk_id);
      setTimeout(() => setCopiedChunkId(null), 2000);
    }
  };

  const handleCardClick = (citation: Citation) => {
    onSelectCitation(activeCitation?.chunk_id === citation.chunk_id ? null : citation);
  };

  const handleKeyDown = (e: React.KeyboardEvent, citation: Citation) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      handleCardClick(citation);
    }
  };

  return (
    <aside
      id="citation-drawer"
      className="drawer-panel"
      role="complementary"
      aria-label="Document Citations Drawer"
    >
      <header className="drawer-header">
        <div className="drawer-title">
          <span>{title}</span>
          <span id="citations-count-badge" className="badge badge-success">
            {citations.length}
          </span>
        </div>
        {onClose && (
          <button
            type="button"
            className="drawer-close-btn"
            onClick={onClose}
            aria-label="Close citation drawer"
          >
            ✕
          </button>
        )}
      </header>

      {citations.length > 0 && (
        <div className="citation-search-box">
          <input
            id="citation-search-input"
            type="search"
            className="citation-search-field"
            placeholder="Filter citations by document or text..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            aria-label="Filter citations"
          />
          {searchTerm && (
            <button
              type="button"
              className="citation-search-clear"
              onClick={() => setSearchTerm("")}
              aria-label="Clear filter search"
            >
              ✕
            </button>
          )}
        </div>
      )}

      {activeCitation && (
        <div
          id="active-citation-inspector"
          className="active-citation-inspector"
          role="region"
          aria-live="polite"
          aria-label="Active Citation Detail"
        >
          <div className="inspector-header">
            <div className="inspector-title">
              <span className="inspector-tag">Active Source Excerpt</span>
              <span className="badge">p. {activeCitation.page_number}</span>
            </div>
            <div className="inspector-actions">
              <button
                id="copy-excerpt-btn"
                type="button"
                className="btn-action-small"
                onClick={(e) => handleCopyExcerpt(activeCitation, e)}
                title="Copy excerpt to clipboard"
                aria-label="Copy citation excerpt to clipboard"
              >
                {copiedChunkId === activeCitation.chunk_id ? "✓ Copied!" : "📋 Copy Excerpt"}
              </button>
              <button
                type="button"
                className="btn-action-small"
                onClick={() => onSelectCitation(null)}
                title="Close excerpt inspector"
                aria-label="Close active citation inspector"
              >
                ✕ Close
              </button>
            </div>
          </div>

          <div className="inspector-doc-meta">
            <span className="doc-filename">📄 {activeCitation.file_name}</span>
            <span className="doc-score">Score: {activeCitation.relevance_score.toFixed(3)}</span>
          </div>

          <blockquote id="active-excerpt-text" className="active-excerpt-blockquote">
            {activeCitation.excerpt}
          </blockquote>

          <div className="inspector-footer">
            <span className="chunk-id-tag">
              Chunk ID: <code>{activeCitation.chunk_id}</code>
            </span>
          </div>
        </div>
      )}

      {citations.length === 0 ? (
        <div id="empty-citations-state" className="empty-citations-card" role="status">
          <div className="empty-state-icon" aria-hidden="true">📚</div>
          <p className="empty-state-title">No Citations Available</p>
          <p id="empty-citations-prompt" className="empty-state-desc">
            No document sources retrieved yet. Submit a query to inspect cited page excerpts.
          </p>
        </div>
      ) : filteredCitations.length === 0 ? (
        <div className="empty-citations-card" role="status">
          <p className="empty-state-desc">
            No citations match "{searchTerm}". Try a different filter term.
          </p>
        </div>
      ) : (
        <div id="citations-list" className="citations-list" role="list" aria-label="Retrieved citations list">
          {filteredCitations.map((c, idx) => {
            const isSelected = activeCitation?.chunk_id === c.chunk_id;
            return (
              <article
                key={`${c.chunk_id}-${idx}`}
                id={`citation-card-${c.chunk_id}`}
                className={`citation-card ${isSelected ? "citation-card-active" : ""}`}
                role="listitem"
                tabIndex={0}
                aria-selected={isSelected}
                aria-label={`Citation from ${c.file_name} page ${c.page_number}`}
                onClick={() => handleCardClick(c)}
                onKeyDown={(e) => handleKeyDown(e, c)}
              >
                <div className="citation-meta">
                  <span className="citation-doc-name">📄 {c.file_name}</span>
                  <span className="badge">p. {c.page_number}</span>
                </div>
                <p className="citation-excerpt-preview">
                  {c.excerpt.length > 120 ? `${c.excerpt.slice(0, 120)}...` : c.excerpt}
                </p>
                <div className="citation-card-footer">
                  <span className="citation-score">Score: {c.relevance_score.toFixed(3)}</span>
                  <span className="citation-chunk-id">ID: {c.chunk_id.slice(0, 8)}</span>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </aside>
  );
};

export default CitationDrawer;
