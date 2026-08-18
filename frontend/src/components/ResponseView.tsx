import React, { useEffect, useRef } from "react";
import { ChatMessage, Citation } from "../types";

export interface ResponseViewProps {
  messages: ChatMessage[];
  isStreaming: boolean;
  onSelectCitation?: (citation: Citation) => void;
  autoScroll?: boolean;
}

export const ResponseView: React.FC<ResponseViewProps> = ({
  messages,
  isStreaming,
  onSelectCitation,
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
        return (
          <article
            key={msg.id}
            id={`message-${msg.id}`}
            className={`message-item ${isUser ? "message-user" : "message-assistant"}`}
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

            {msg.finops && (
              <footer className="finops-bar" aria-label="Execution metrics">
                <span>Tokens: {msg.finops.total_tokens}</span>
                <span>Cost: ${msg.finops.estimated_cost_usd.toFixed(5)}</span>
                <span>Time: {msg.finops.execution_time_seconds.toFixed(2)}s</span>
                {msg.finops.is_cached && <span className="cache-hit-tag">(Cache Hit)</span>}
              </footer>
            )}
          </article>
        );
      })}
      <div ref={messagesEndRef} id="streaming-anchor" aria-hidden="true" />
    </div>
  );
};
