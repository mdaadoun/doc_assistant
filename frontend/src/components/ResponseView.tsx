import React from "react";
import { ChatMessage } from "../types";

interface ResponseViewProps {
  messages: ChatMessage[];
  isStreaming: boolean;
}

export const ResponseView: React.FC<ResponseViewProps> = ({
  messages,
  isStreaming,
}) => {
  if (messages.length === 0) {
    return (
      <div className="messages-list" style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{ textAlign: "center", color: "var(--text-muted)", maxWidth: "420px" }}>
          <p style={{ fontWeight: 600, color: "var(--text-secondary)", marginBottom: "6px" }}>
            Ready for Knowledge Retrieval
          </p>
          <p style={{ fontSize: "0.85rem" }}>
            Ask questions regarding enterprise policy, specifications, and contracts.
            Answers are strictly grounded with page-level citations.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="messages-list">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`message-item ${
            msg.sender === "user" ? "message-user" : ""
          }`}
        >
          <div className="message-header">
            <span>{msg.sender === "user" ? "👤 User Query" : "🤖 Grounded Assistant"}</span>
            <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
              {msg.confidenceScore !== undefined && (
                <span
                  className={`badge ${
                    msg.confidenceScore >= 0.35 ? "badge-success" : "badge-warning"
                  }`}
                >
                  Conf: {(msg.confidenceScore * 100).toFixed(1)}%
                </span>
              )}
              <span>{msg.timestamp}</span>
            </div>
          </div>

          <div style={{ whiteSpace: "pre-wrap", color: "var(--text-primary)" }}>
            {msg.content}
            {msg.isStreaming && <span style={{ opacity: 0.6 }}> ▌</span>}
          </div>

          {msg.finops && (
            <div
              style={{
                marginTop: "12px",
                paddingTop: "8px",
                borderTop: "1px solid var(--border-subtle)",
                display: "flex",
                gap: "16px",
                fontSize: "0.72rem",
                color: "var(--text-muted)",
              }}
            >
              <span>Tokens: {msg.finops.total_tokens}</span>
              <span>Cost: ${msg.finops.estimated_cost_usd.toFixed(5)}</span>
              <span>Time: {msg.finops.execution_time_seconds.toFixed(2)}s</span>
              {msg.finops.is_cached && <span>(Cache Hit)</span>}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
