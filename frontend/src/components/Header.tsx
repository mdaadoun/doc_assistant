import React from "react";

interface HeaderProps {
  conversationId: string;
  isBackendConnected: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  conversationId,
  isBackendConnected,
}) => {
  return (
    <header className="app-header">
      <div className="brand-section">
        <h1 className="brand-title">Corporate Document Assistant</h1>
        <p className="brand-subtitle">
          Grounded RAG Platform with verified page citations and strict confidence gating
        </p>
      </div>

      <div className="header-status">
        <span
          className={`badge ${
            isBackendConnected ? "badge-success" : "badge-warning"
          }`}
          title="Backend Service Health"
        >
          ● {isBackendConnected ? "System Online" : "Connecting..."}
        </span>
        <span className="badge" title="Active Session ID">
          Session: {conversationId.slice(0, 8)}
        </span>
      </div>
    </header>
  );
};
