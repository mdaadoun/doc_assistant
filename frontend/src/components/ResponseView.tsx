import React, { useEffect, useRef } from "react";
import { ChatMessage, Citation, RetrievalPhase } from "../types";
import { ConfidenceIndicator } from "./ConfidenceIndicator";
import { LoadingIndicator } from "./LoadingIndicator";

export interface ResponseViewProps {
  messages: ChatMessage[];
  isStreaming: boolean;
  onSelectCitation?: (citation: Citation) => void;
  onRetryMessage?: (query: string, topK?: number) => void;
  retrievalPhase?: RetrievalPhase;
  autoScroll?: boolean;
}

export const ResponseView: React.FC<ResponseViewProps> = ({
  messages,
  isStreaming,
  onSelectCitation,
  onRetryMessage,
  retrievalPhase = "idle",
  autoScroll = true,
}) => {
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (autoScroll) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isStreaming, autoScroll]);

  if (messages.length === 0) {
    return (
      <div
        id="response-view"
        className="messages-list messages-empty"
        role="log"
        aria-live="polite"
        aria-label="Conversation history"
      >
        <div id="empty-state-prompt" className="empty-state-card">
          <div className="empty-state-icon">📖</div>
          <p className="empty-state-title">Ready for Grounded Knowledge Retrieval</p>
          <p className="empty-state-desc">
            Ask questions regarding enterprise policy, specifications, and contracts.
            All answers are strictly grounded with page-level citations.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      id="response-view"
      className="messages-list"
      role="log"
      aria-live="polite"
      aria-atomic="false"
      aria-label="Conversation message stream"
    >
      {messages.map((msg) => {
        const isUser = msg.sender === "user";
        const hasError = !!msg.error;
        const isAwaitingFirstToken =
          msg.isStreaming && !msg.content && !hasError;

        return (
          <article
            key={msg.id}
            id={`message-${msg.id}`}
            className={`message-item ${
              isUser ? "message-user" : "message-assistant"
            } ${hasError ? "message-has-error" : ""}`}
            aria-label={`${isUser ? "User" : "Assistant"} message at ${msg.timestamp}`}
          >
            <header className="message-header">
              <span className="message-sender">
                {isUser ? "👤 User Query" : "🤖 Grounded Assistant"}
              </span>
              <div className="message-header-badges">
                {msg.grounded !== undefined && (
                  <span
                    className={`badge ${
                      msg.grounded ? "badge-success" : "badge-warning"
                    }`}
                  >
                    {msg.grounded ? "Grounded" : "Ungrounded"}
                  </span>
                )}
                {msg.confidenceScore !== undefined && (
                  <span
                    className={`badge ${
                      msg.confidenceScore >= 0.35 ? "badge-success" : "badge-warning"
                    }`}
                  >
                    Conf: {(msg.confidenceScore * 100).toFixed(1)}%
                  </span>
                )}
                <time className="message-timestamp">{msg.timestamp}</time>
              </div>
            </header>

            {/* In-flight retrieval loading skeleton */}
            {isAwaitingFirstToken && (
              <LoadingIndicator
                phase={msg.retrievalPhase || retrievalPhase || "retrieving"}
              />
            )}

            {/* Error Message Card with Retry */}
            {hasError && (
              <div className="message-error-card" role="alert">
                <div className="message-error-header">
                  <span className="error-icon" aria-hidden="true">⚠️</span>
                  <span className="error-title">Execution Error</span>
                  {msg.error?.code && (
                    <span className="badge badge-error-code">
                      {msg.error.code}
                    </span>
                  )}
                </div>
                <p className="message-error-detail">
                  {msg.error?.message || "An unexpected error occurred."}
                </p>
                {msg.error?.retryable !== false && onRetryMessage && msg.error?.query && (
                  <button
                    id="message-retry-btn"
                    type="button"
                    className="btn-retry"
                    onClick={() =>
                      onRetryMessage(msg.error!.query!, msg.error!.topK)
                    }
                    aria-label="Retry this query"
                  >
                    <span aria-hidden="true">🔄</span> Retry
                  </button>
                )}
              </div>
            )}

            {/* Message Body Content */}
            {msg.content && (
              <div className="message-body">
                <span className="message-text">{msg.content}</span>
                {msg.isStreaming && (
                  <span
                    id="streaming-cursor"
                    className="streaming-cursor"
                    aria-hidden="true"
                  >
                    ▌
                  </span>
                )}
              </div>
            )}

            {/* Confidence indicator component with progress bar */}
            {!isUser && msg.confidenceScore !== undefined && !hasError && (
              <div className="message-confidence-section">
                <ConfidenceIndicator
                  confidenceScore={msg.confidenceScore}
                  grounded={msg.grounded}
                  showMeter={true}
                />
              </div>
            )}

            {/* Inline Citations */}
            {msg.citations && msg.citations.length > 0 && (
              <div className="message-citations" aria-label="Message sources">
                <span className="citations-label">Sources:</span>
                {msg.citations.map((citation, idx) => (
                  <button
                    key={`${citation.chunk_id}-${idx}`}
                    type="button"
                    className="citation-pill"
                    onClick={() => onSelectCitation?.(citation)}
                    title={`View citation excerpt from ${citation.file_name} (Page ${citation.page_number})`}
                  >
                    📄 {citation.file_name} (p.{citation.page_number})
                  </button>
                ))}
              </div>
            )}

            {/* FinOps Telemetry */}
            {msg.finops && (
              <footer className="finops-bar" aria-label="Execution metrics">
                <span>Tokens: {msg.finops.total_tokens}</span>
                <span>Cost: ${msg.finops.estimated_cost_usd.toFixed(5)}</span>
                <span>Time: {msg.finops.execution_time_seconds.toFixed(2)}s</span>
                {msg.finops.is_cached && (
                  <span className="cache-hit-tag">(Cache Hit)</span>
                )}
              </footer>
            )}
          </article>
        );
      })}
      <div ref={messagesEndRef} id="streaming-anchor" aria-hidden="true" />
    </div>
  );
};

export default ResponseView;
