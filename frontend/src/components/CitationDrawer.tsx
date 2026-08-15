import React from "react";
import { Citation } from "../types";

interface CitationDrawerProps {
  citations: Citation[];
  activeCitation: Citation | null;
  onSelectCitation: (citation: Citation) => void;
}

export const CitationDrawer: React.FC<CitationDrawerProps> = ({
  citations,
  activeCitation,
  onSelectCitation,
}) => {
  return (
    <aside className="drawer-panel">
      <div className="drawer-title">
        <span>Grounded Citations</span>
        <span className="badge">{citations.length}</span>
      </div>

      {citations.length === 0 ? (
        <p style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
          No document sources retrieved yet. Submit a query to inspect cited page
          excerpts.
        </p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
          {citations.map((c, idx) => {
            const isSelected =
              activeCitation?.chunk_id === c.chunk_id;
            return (
              <div
                key={`${c.chunk_id}-${idx}`}
                className="citation-card"
                onClick={() => onSelectCitation(c)}
                style={{
                  borderColor: isSelected
                    ? "var(--border-focus)"
                    : "var(--border-subtle)",
                }}
              >
                <div className="citation-meta">
                  <span>📄 {c.file_name}</span>
                  <span>p. {c.page_number}</span>
                </div>
                <p
                  style={{
                    color: "var(--text-secondary)",
                    fontFamily: "var(--font-mono)",
                    fontSize: "0.78rem",
                    lineHeight: 1.4,
                  }}
                >
                  {c.excerpt.length > 120
                    ? `${c.excerpt.slice(0, 120)}...`
                    : c.excerpt}
                </p>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    marginTop: "6px",
                    fontSize: "0.7rem",
                    color: "var(--text-muted)",
                  }}
                >
                  <span>Score: {c.relevance_score.toFixed(3)}</span>
                  <span>ID: {c.chunk_id.slice(0, 8)}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </aside>
  );
};
