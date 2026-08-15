import React, { useState } from "react";

interface QueryInputProps {
  onSubmit: (query: string, topK: number) => void;
  isLoading: boolean;
}

export const QueryInput: React.FC<QueryInputProps> = ({
  onSubmit,
  isLoading,
}) => {
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(5);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;
    onSubmit(query.trim(), topK);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form className="input-section" onSubmit={handleSubmit}>
      <div className="input-row">
        <textarea
          className="query-textarea"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about uploaded corporate documents..."
          rows={2}
          disabled={isLoading}
        />
        <button
          type="submit"
          className="btn-primary"
          disabled={isLoading || !query.trim()}
        >
          {isLoading ? "Querying..." : "Send Query"}
        </button>
      </div>

      <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
        <label
          style={{
            fontSize: "0.8rem",
            color: "var(--text-secondary)",
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}
        >
          Context Chunks (top_k):
          <select
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
            disabled={isLoading}
            style={{
              background: "var(--bg-app)",
              color: "var(--text-primary)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "var(--radius-sm)",
              padding: "2px 8px",
              fontSize: "0.8rem",
            }}
          >
            <option value={3}>3</option>
            <option value={5}>5 (Default)</option>
            <option value={10}>10</option>
          </select>
        </label>
      </div>
    </form>
  );
};
