import React from "react";
import { RetrievalPhase } from "../types";

export interface LoadingIndicatorProps {
  phase?: RetrievalPhase;
  message?: string;
  elapsedSeconds?: number;
  className?: string;
}

const PHASE_LABELS: Record<RetrievalPhase, string> = {
  idle: "Idle",
  retrieving: "Dual Retrieval (Dense Vector + BM25 Sparse Search)...",
  reranking: "Cross-Encoder Re-Ranking & Confidence Gating (S_min >= 0.35)...",
  generating: "Grounded LLM Generation & Citation Extraction...",
  complete: "Completed",
  error: "Error encountered",
};

export const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  phase = "retrieving",
  message,
  elapsedSeconds,
  className = "",
}) => {
  const displayLabel = message || PHASE_LABELS[phase] || "Processing query...";

  return (
    <div
      id="loading-indicator"
      className={`loading-indicator-card ${className}`}
      role="status"
      aria-live="polite"
      aria-busy="true"
      aria-label="Query processing status"
    >
      <div className="loading-indicator-header">
        <div className="loading-status-row">
          <span id="loading-spinner" className="btn-spinner loading-spinner" aria-hidden="true" />
          <span id="retrieval-phase-label" className="phase-label">
            {displayLabel}
          </span>
        </div>
        {elapsedSeconds !== undefined && elapsedSeconds > 0 && (
          <span className="elapsed-time-badge">
            {elapsedSeconds.toFixed(1)}s
          </span>
        )}
      </div>

      <div id="loading-step-list" className="loading-steps-track" aria-label="Pipeline steps">
        <div
          className={`step-item ${
            phase === "retrieving" ? "step-active" : phase !== "idle" ? "step-done" : ""
          }`}
        >
          <span className="step-number">1</span>
          <span className="step-title">Dual Search</span>
        </div>
        <div className="step-divider" />
        <div
          className={`step-item ${
            phase === "reranking" ? "step-active" : ["generating", "complete"].includes(phase) ? "step-done" : ""
          }`}
        >
          <span className="step-number">2</span>
          <span className="step-title">Re-Rank & Guard</span>
        </div>
        <div className="step-divider" />
        <div
          className={`step-item ${
            phase === "generating" ? "step-active" : phase === "complete" ? "step-done" : ""
          }`}
        >
          <span className="step-number">3</span>
          <span className="step-title">Grounded Stream</span>
        </div>
      </div>

      <div
        id="loading-skeleton-pulse"
        className="loading-skeleton-pulse"
        aria-hidden="true"
      >
        <div className="skeleton-line skeleton-line-title" />
        <div className="skeleton-line skeleton-line-body" />
        <div className="skeleton-line skeleton-line-short" />
      </div>
    </div>
  );
};

export default LoadingIndicator;
