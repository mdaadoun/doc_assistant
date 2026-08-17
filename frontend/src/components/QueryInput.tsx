import React, { useState, useRef } from "react";

export interface QueryInputProps {
  onSubmit: (query: string, topK: number) => void;
  isLoading: boolean;
  disabled?: boolean;
  placeholder?: string;
  initialTopK?: number;
  maxQueryLength?: number;
  suggestedQueries?: string[];
}

const DEFAULT_SUGGESTIONS: string[] = [
  "Summarize the key contractual obligations and SLAs.",
  "What are the compliance and data retention requirements?",
  "List all termination clauses and notice periods.",
];

export const QueryInput: React.FC<QueryInputProps> = ({
  onSubmit,
  isLoading,
  disabled = false,
  placeholder = "Ask a question about uploaded corporate documents...",
  initialTopK = 5,
  maxQueryLength = 4000,
  suggestedQueries = DEFAULT_SUGGESTIONS,
}) => {
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(initialTopK);
  const [validationError, setValidationError] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const isInteractiveDisabled = isLoading || disabled;
  const isQueryEmpty = !query.trim();

  const handleValidation = (value: string): boolean => {
    if (value.length > maxQueryLength) {
      setValidationError(`Query exceeds ${maxQueryLength} character limit.`);
      return false;
    }
    setValidationError(null);
    return true;
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newVal = e.target.value;
    setQuery(newVal);
    handleValidation(newVal);
  };

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const trimmed = query.trim();

    if (!trimmed || isInteractiveDisabled) return;
    if (!handleValidation(trimmed)) return;

    onSubmit(trimmed, topK);
    setQuery("");
    setValidationError(null);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    } else if (e.key === "Escape" && query) {
      e.preventDefault();
      setQuery("");
      setValidationError(null);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    if (isInteractiveDisabled) return;
    setQuery(suggestion);
    setValidationError(null);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  const handleClear = () => {
    setQuery("");
    setValidationError(null);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  return (
    <form
      id="query-form"
      role="form"
      aria-label="Document Query Form"
      className="input-section"
      onSubmit={handleSubmit}
    >
      {suggestedQueries && suggestedQueries.length > 0 && !query && (
        <div className="suggested-queries-wrapper" aria-label="Suggested Prompts">
          <span className="suggested-label">Suggested:</span>
          <div className="suggested-queries-list">
            {suggestedQueries.map((item, idx) => (
              <button
                key={idx}
                type="button"
                className="suggested-query-btn"
                onClick={() => handleSuggestionClick(item)}
                disabled={isInteractiveDisabled}
                aria-label={`Use suggestion: ${item}`}
              >
                {item}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="input-row">
        <textarea
          id="query-input"
          ref={textareaRef}
          className={`query-textarea ${validationError ? "textarea-error" : ""}`}
          value={query}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          rows={2}
          disabled={isInteractiveDisabled}
          aria-label="Corporate document query input"
          aria-invalid={validationError !== null}
          aria-describedby={validationError ? "query-validation-error" : undefined}
          maxLength={maxQueryLength + 50}
        />

        <div className="input-action-buttons">
          {query.length > 0 && !isInteractiveDisabled && (
            <button
              id="clear-query-btn"
              type="button"
              className="btn-clear"
              onClick={handleClear}
              aria-label="Clear query input"
              title="Clear input (Esc)"
            >
              ✕
            </button>
          )}

          <button
            id="submit-query-btn"
            type="submit"
            className="btn-primary"
            disabled={isInteractiveDisabled || isQueryEmpty}
            aria-label={isLoading ? "Submitting query..." : "Send query"}
            aria-busy={isLoading}
          >
            {isLoading ? (
              <>
                <span className="btn-spinner" aria-hidden="true" />
                <span>Querying...</span>
              </>
            ) : (
              <span>Send Query</span>
            )}
          </button>
        </div>
      </div>

      {validationError && (
        <div id="query-validation-error" className="input-error-msg" role="alert">
          {validationError}
        </div>
      )}

      <div className="input-controls-bar">
        <label
          htmlFor="top-k-select"
          className="control-label"
          aria-label="Context Chunks top_k selection"
        >
          <span>Context Chunks (top_k):</span>
          <select
            id="top-k-select"
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
            disabled={isInteractiveDisabled}
            className="top-k-dropdown"
            aria-label="Number of context chunks to retrieve"
          >
            <option value={3}>3 chunks</option>
            <option value={5}>5 chunks (Recommended)</option>
            <option value={10}>10 chunks</option>
            <option value={15}>15 chunks (Deep search)</option>
          </select>
        </label>

        <div className="input-hints">
          <span className="char-counter" aria-label="Character count">
            {query.length} / {maxQueryLength}
          </span>
          <span className="keyboard-hint" aria-hidden="true">
            ↵ to send &bull; Shift+↵ for new line
          </span>
        </div>
      </div>
    </form>
  );
};

export default QueryInput;
