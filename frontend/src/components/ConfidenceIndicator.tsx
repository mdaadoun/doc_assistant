import React from "react";
import { ConfidenceTier } from "../types";

export interface ConfidenceIndicatorProps {
  confidenceScore: number;
  grounded?: boolean;
  showMeter?: boolean;
  compact?: boolean;
  className?: string;
}

export function getConfidenceTier(score: number): {
  tier: ConfidenceTier;
  label: string;
  badgeClass: string;
} {
  if (score >= 0.7) {
    return {
      tier: "high",
      label: "High Confidence",
      badgeClass: "badge-confidence-high",
    };
  }
  if (score >= 0.35) {
    return {
      tier: "medium",
      label: "Moderate Confidence",
      badgeClass: "badge-confidence-medium",
    };
  }
  return {
    tier: "low",
    label: "Low Confidence / Refusal",
    badgeClass: "badge-confidence-low",
  };
}

export const ConfidenceIndicator: React.FC<ConfidenceIndicatorProps> = ({
  confidenceScore,
  grounded = true,
  showMeter = true,
  compact = false,
  className = "",
}) => {
  const percentage = Math.min(100, Math.max(0, confidenceScore * 100));
  const { tier, label, badgeClass } = getConfidenceTier(confidenceScore);
  const isGroundedThresholdMet = confidenceScore >= 0.35;

  if (compact) {
    return (
      <div
        id="confidence-indicator"
        className={`confidence-indicator confidence-compact ${className}`}
        aria-label={`Confidence score ${(confidenceScore * 100).toFixed(1)}%, ${label}`}
      >
        <span
          id="confidence-score-badge"
          className={`badge ${badgeClass}`}
          title={`Relevance score: ${confidenceScore.toFixed(3)} (S_min >= 0.35)`}
        >
          Conf: {(confidenceScore * 100).toFixed(1)}%
        </span>
        {grounded !== undefined && (
          <span
            id="grounded-status-badge"
            className={`badge ${grounded ? "badge-success" : "badge-warning"}`}
          >
            {grounded ? "Grounded" : "Ungrounded"}
          </span>
        )}
      </div>
    );
  }

  return (
    <div
      id="confidence-indicator"
      className={`confidence-indicator confidence-full ${className}`}
      role="region"
      aria-label="Confidence and grounding indicator"
    >
      <div className="confidence-header">
        <div className="confidence-badges-row">
          <span
            id="confidence-tier-badge"
            className={`badge ${badgeClass}`}
            data-tier={tier}
          >
            {label}
          </span>
          <span id="confidence-score-badge" className="badge badge-score">
            {(confidenceScore * 100).toFixed(1)}% (
            {confidenceScore.toFixed(3)})
          </span>
          <span
            id="grounded-status-badge"
            className={`badge ${
              grounded && isGroundedThresholdMet ? "badge-success" : "badge-warning"
            }`}
          >
            {grounded && isGroundedThresholdMet
              ? "✓ Verified Grounded"
              : "⚠ Grounding Warning"}
          </span>
        </div>
      </div>

      {showMeter && (
        <div className="confidence-meter-container">
          <div
            id="confidence-meter-bar"
            className={`confidence-meter-track confidence-meter-${tier}`}
            role="progressbar"
            aria-valuenow={Math.round(percentage)}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label="Confidence score meter"
          >
            <div
              className="confidence-meter-fill"
              style={{ width: `${percentage}%` }}
            />
            <div
              id="confidence-threshold-marker"
              className="confidence-threshold-marker"
              title="Minimum Confidence Threshold (S_min = 0.35)"
              style={{ left: "35%" }}
            />
          </div>
          <div className="confidence-meter-labels">
            <span className="meter-min">0%</span>
            <span className="meter-threshold-label">Threshold (35%)</span>
            <span className="meter-max">100%</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConfidenceIndicator;
