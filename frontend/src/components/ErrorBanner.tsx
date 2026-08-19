import React from "react";
import { ErrorInfo } from "../types";

export interface ErrorBannerProps {
  error: ErrorInfo | string | null;
  onRetry?: () => void;
  onDismiss?: () => void;
  title?: string;
  className?: string;
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({
  error,
  onRetry,
  onDismiss,
  title = "Query Execution Failed",
  className = "",
}) => {
  if (!error) return null;

  const errorMessage = typeof error === "string" ? error : error.message;
  const errorCode = typeof error === "string" ? "ERROR" : error.code || "UNKNOWN_ERROR";
  const retryable = typeof error === "string" ? true : error.retryable !== false;
  const timestamp = typeof error === "string" ? undefined : error.timestamp;

  return (
    <div
      id="error-banner"
      className={`error-banner-container ${className}`}
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div className="error-banner-header">
        <div className="error-title-wrapper">
          <span className="error-icon" aria-hidden="true">
            ⚠️
          </span>
          <strong id="error-title" className="error-title">
            {title}
          </strong>
          <span id="error-code-badge" className="badge badge-error-code">
            {errorCode}
          </span>
        </div>

        {onDismiss && (
          <button
            id="dismiss-error-btn"
            type="button"
            className="btn-dismiss"
            onClick={onDismiss}
            aria-label="Dismiss error banner"
            title="Dismiss error"
          >
            ✕
          </button>
        )}
      </div>

      <div className="error-banner-body">
        <p id="error-message-text" className="error-message-text">
          {errorMessage}
        </p>
      </div>

      <div id="error-banner-actions" className="error-banner-actions">
        {retryable && onRetry && (
          <button
            id="retry-button"
            type="button"
            className="btn-retry"
            onClick={onRetry}
            aria-label="Retry failed query"
          >
            <span aria-hidden="true">🔄</span> Retry Query
          </button>
        )}

        {timestamp && (
          <time className="error-timestamp">Occurred at {timestamp}</time>
        )}
      </div>
    </div>
  );
};

export default ErrorBanner;
